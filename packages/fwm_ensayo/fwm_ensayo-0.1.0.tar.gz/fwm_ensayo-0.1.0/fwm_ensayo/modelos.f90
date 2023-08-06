!Modelos: acoplado con cuencas presenta una serie de modelos hidrologicos distribuidos
!Copyright (C) <2014>  <Nicolas Velasquez Giron>

!This program is free software: you can redistribute it and/or modify
!it under the terms of the GNU General Public License as published by
!the Free Software Foundation, either version 3 of the License, or
!(at your option) any later version.

!This program is distributed in the hope that it will be useful,
!but WITHOUT ANY WARRANTY; without even the implied warranty of
!MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!GNU General Public License for more details.

!You should have received a copy of the GNU General Public License
!along with this program.  If not, see <http://www.gnu.org/licenses/>.

module modelos

!La lluvia es controlada por el modulo lluvia.
!use lluvia

!Todas las variables tienen que ser definidas dentro del modulo
implicit none

!-----------------------------------------------------------------------
!Variableses globales para la modelacion
!-----------------------------------------------------------------------
!Variables de la cuenca 
real xll,yll !coordenadas de la esquina inferior izquierda
real noData !Valor que representa los no datos
real dx !Largo del mapa leido
real dxP !largo proyectado del mapa, debe ser indicado si no se cononce
real dt !Delta del tiempo de modelacion
integer ncols,nrows !cantidad de columnas y filas del mapa
integer nceldas !Cantidad de celdas que componen la cuenca
!Variables de mapas que pueden ser usados por modelos
integer, allocatable :: tipo_celda(:,:),acum_cel(:,:) !Tipo de celda y area acumulada
integer, allocatable :: drena(:,:) !Indicador de la topologia de la cuenca 
real, allocatable :: L_celda(:,:),pend_celda(:,:) !Long celda, pend de celda
real, allocatable :: pend_cauce(:,:),Elev(:,:),X(:,:),Y(:,:) !pend de cauce, elevacion, coordenadas
real, allocatable :: Hu(:,:),H3(:,:),Man(:,:) !Alm capilar, Alm maximo sub-sup, Manning
real, allocatable :: Ks(:,:),Kp(:,:),EVP(:,:) !Cond sub-sup, Cond supterranea, EV potencial
!conversores de las variables ks y kp
real conver_ks,conver_kp !Conversores de unidades de ks y kp
!Variables de control 
integer, allocatable :: control(:,:) !Celdas de la cuenca que tienen puntos de control
integer, allocatable :: control_h(:,:) !Celdas de la cuenca que son puntos de control de humedad
!Variables de mapas modelo shia
real, allocatable :: part_ocg(:,:) !Ecuaciones OCG (onda cinematica geomorfologica)
real, allocatable :: S(:,:) !Almacenamiento de los 5 tanques del modelo
!Variables de evaluacion
integer eval !Variable de evaluacion de que las variables necesarias para el modelo estan asignadas
!Variables de lluvia
real, allocatable :: coord(:,:) !Variable con las coordenadas de las estaciones de lluvia
integer, allocatable :: tin(:,:) !Variable que contiene los triangulos conformados a partir de las coordenadas
integer, allocatable :: tin_perte(:,:) !Variable con la pertenencia de los triangulos
real, allocatable :: lluvia(:,:) !Registros de lluvia
real, allocatable :: evp_p(:,:) !Registros de evp tomados de series
!Variables de regionalizacion del flujo
real epsilo,exp1 !coeficiente manning y exponente manning en carcavas [0.5, 0.64]

contains

!-----------------------------------------------------------------------
!Funciones Varias
!-----------------------------------------------------------------------
!Funciones para estimar variables del modelo
subroutine OCG_params(params,exp_param,calculo_ocg)
    !Variables de entrada
    real, intent(in) :: params(9) ! c1, Omega, k, alfa1, alfa2, sigma1, sigma2, sigma3, fhi
    real, intent(out) :: exp_param(4) !los cuatro parametros para la onda, e_cau,e_pend,e_acum,B
    integer, intent(out) :: calculo_ocg !0 si si la calculo, 1 si no
    !f2py intent(in) :: params
    !f2py intent(out) :: exp_param,calculo_ocg 
    !Internos 
    real c1, Omega, k, alfa1, alfa2, sigma1, sigma2, sigma3, fhi 
    real e_cau,e_pend,e_acum,B,e_B
    !Copia params
    sigma1=params(1); sigma2=params(2); sigma3=params(3)
    Omega=params(4); alfa1=params(5); alfa2=params(6)
    k=params(7); fhi=params(8); c1=params(9)
    !Calcula los exponentes y el coeficiente de la OGC
    B=Omega*(c1*k**(alfa1-alfa2))**((2/3)-sigma2)
    e_B=1/(1+alfa2*(0.667-sigma2))
    e_cau=(0.667-sigma2)*(1-alfa2)*e_B
    e_pend=(0.5-sigma3)*e_B
    e_acum=(fhi*(0.667-sigma2)*(alfa2-alfa1)+sigma1)*e_B
    e_B=-1*e_B
    B=B**e_B
    exp_param(1)=e_cau; exp_param(2)=e_pend; exp_param(3)=e_acum; exp_param(4)=B 
    !si la variable de area acumulada y pendiente se encuentran alojadas calcula vn=(Area**OCG(1)) --> *(So**OCG(2))*(Ac**OCG(3))*OCG(4) ![m/seg]
    if (allocated(pend_cauce).and.allocated(pend_celda).and.allocated(acum_cel).and.nceldas.gt.0) then
	!se fija si la variable ya ha sido alojada o no
	if (allocated(part_ocg) .eqv. .false.) then
	    allocate(part_ocg(1,nceldas))
	endif
	part_ocg(1,:)=noData
	where(tipo_celda(1,:).gt.1) part_ocg(1,:)=(pend_celda(1,:)**e_pend)*(((acum_cel(1,:)*(dxP**2))/1e6)**e_acum)*B ![adim]
	!where(tipo_celda(1,:).eq.3) part_ocg(1,:)=(pend_cauce(1,:)**e_pend)*(((acum_cel(1,:)*(dxP**2))/1e6)**e_acum)*B ![adim]
	calculo_ocg=0
    else
	calculo_ocg=1
    endif
end subroutine
!verificador del modelo shia
subroutine shia_verify
    eval=0
    if (allocated(tipo_celda).and.allocated(drena).and.allocated(L_celda).and.allocated(pend_celda)&
    &.and.allocated(pend_cauce).and.allocated(X).and.allocated(Y).and.allocated(Hu)&
    &.and.allocated(Man).and.allocated(ks).and.allocated(kp).and.allocated(evp).and.allocated(S)) then
	eval=1
    endif
end subroutine
subroutine pre_tin_points_select(resultado,nceldas) !Arroja una matriz donde se indica a que triangulo pertenece cada celda 
    !Variables de entrada
    integer, intent(in) :: nceldas
    !Variables de salida
    integer, intent(out) :: resultado
    !f2py intent(in) :: nceldas
    !f2py intent(out) :: resultado
    !Variables locales
    integer i,j,flag,flag2,cont,N_tin,n(2)
    real ori1,ori2,ori3,oriP,xp,yp,x1,x2,x3,y1,y2,y3
    !Comienza la busqueda de pertenencia para cada entrada de la tabla
    if (allocated(tin_perte).eqv. .false.) then
	allocate(tin_perte(1,nceldas))
    endif
    flag2=0
    cont=0
    resultado=0
    n=shape(tin)
    N_tin=n(2)
    tin_perte=noData
    do i=1,nceldas
	!Inicializa una bandera que revisa si el punto se encuentra dentro de algún triangulo
	flag=0
	!Comienza a buscar el triangulo de pertenencia
	j=1
	do while (j.le.N_tin .and. flag.eq.0)
	    !Cambio de variables para programar facil
	    xp=x(1,i); yp=y(1,i)
	    x1=coord(1,TIN(1,j)); x2=coord(1,TIN(2,j)); x3=coord(1,TIN(3,j))
	    y1=coord(2,TIN(1,j)); y2=coord(2,TIN(2,j)); y3=coord(2,TIN(3,j))
	    !Calcula la orientación del triangulo    
	    oriP=(x1-x3)*(y2-y3)-(y1-y3)*(x2-x3)
	    ori1=(x1-xp)*(y2-yp)-(y1-yp)*(x2-xp)
	    ori2=(xp-x3)*(y2-y3)-(yp-y3)*(x2-x3)
	    ori3=(x1-x3)*(yp-y3)-(y1-y3)*(xp-x3)
	    !Si las cuatro orientaciones son o positivas o negativas el punto se encuentra dentro
	    if ((oriP.gt.0 .and. ori1.gt.0 .and. ori2.gt.0 .and. ori3.gt.0) .or. (oriP.lt.0 .and. ori1.lt.0 &
	    &.and. ori2.lt.0 .and. ori3.lt.0)) then
		tin_perte(1,i)=j
		flag=1
	    else
		j=j+1
	    end if
	end do
    end do
end subroutine


!-----------------------------------------------------------------------
!Versiones modelo shia
!-----------------------------------------------------------------------

!model_tin_lk: Modelo shia completo, contiene: velocidad lineal en ladera 
!y velocidad cinematica en canal, no se usa la OCG. la lluvia es interpolada
!por idw o tin de acuerdo a lo indicado.
subroutine shia_tin_lk(calib,N_cel,N_cont,N_reg,Q,balance,mean_rain,sp)
    !Variables de entrada
    integer, intent(in) :: N_cel,N_reg,N_cont
    real, intent(in) :: calib(9)
    !Variables de salia
    real, intent(out) :: Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),balance
    !Variables locales 
    real tiempo_ejec(2),tiempo_result !variables de tiempo de ejecucion del programa
    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
    integer drenaid,Res !Vector con el id a donde drena cada celda
    real Rain,rain_sum,pot_local !campo de lluvia  para el intervalo de tiempo, potencial para idw local,
    character*3 corr !local de si se va a hacer correccion o no.
    real Hu_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
    real R1,R2,R3,R4,R5 !lluvia (R1) y flujo que drena por los tanques
    real v_ladera(nceldas),v_cauce(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
    real ax(nceldas),ay(nceldas),bx(nceldas),by(nceldas),cx(nceldas),cy(nceldas),dx(nceldas),dy(nceldas)
    real det1,det2,det3,det4,az,bz,cz,Cel_x,Cel_y,coef1(nceldas),coef2 !Variables de interpolacion tin
    integer Cel_pert !Variables de interpolacion tin
    real m3_mm !Variable para convertir m3 a mm2
    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
    integer i,control_cont,cont !iterador,contador de puntos de control, contador de lluvia faltante    
    !Definiciones para f2py
    !f2py intent(in) :: N_cel,N_reg,N_cont,calib
    !f2py intent(out) :: Q,sp,mean_rain,balance
    !Preambulo a la ejecucion del modelo
    !Calcula la cantidad de agua que es retenida en el capilar
    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
    !Calcula las velocidades horizontales iniciales
    v_ladera=1.4*Calib(4)*(pend_celda(1,:)**0.5)/man(1,:) ![m/s] Vel ladera, Estado constante
    v_cauce=1 ![m/s] Vel ladera, Estado constante
    pend_man=(pend_celda(1,:)**(0.5))/man(1,:)
    ksh=ks(1,:)*Calib(6)*(conver_ks/1000)*pend_celda(1,:) ![m/s] Vel sub-superficial, Estado constante		
    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
    !Calcula el porcentaje de flujo horizontal saliente de cada celda
    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))
    !Calcula las constantes para interpolacion por TIN
    ax=coord(1,tin(1,tin_perte(1,:))) ; ay=coord(2,tin(1,tin_perte(1,:)))
    bx=coord(1,tin(2,tin_perte(1,:))) ; by=coord(2,tin(2,tin_perte(1,:)))
    cx=coord(1,tin(3,tin_perte(1,:))) ; cy=coord(2,tin(3,tin_perte(1,:)))
    coef1=(bx-ax)*(cy-ay)-(cx-ax)*(by-ay)
    !Convertor de mm a mt3 para obtener caudal a la salida
    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
    !Establece el almacenamiento inicial 
    Sp=S
    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
    inicial=sum(Sp(:,:))
    entradas=0
    salidas=0
    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
    mean_rain=0
    if (eval.eq.1) then
	!Calcula el tiempo inicial
	call etime(tiempo_ejec,tiempo_result)
	!Itera para cada intervalo de tiempo
	do tiempo=1,N_reg
	    !Reinicia el conteo de la lluvia y el contador de los puntos de control
	    rain_sum=0
	    control_cont=2	    	    
	    !Itera para todas las celdas
	    do celdas=1,N_cel
		!Interpola la lluvia
		Cel_pert=tin_perte(1,celdas)
		Cel_x=x(1,celdas) ; Cel_y=y(1,celdas)
		az=max(lluvia(tin(1,Cel_pert),tiempo),0.0)
		bz=max(lluvia(tin(2,Cel_pert),tiempo),0.0)
		cz=max(lluvia(tin(3,Cel_pert),tiempo),0.0)
		det1=(cx(celdas)-ax(celdas))*(Cel_y-ay(celdas)) 
		det2=(by(celdas)-ay(celdas))*(Cel_x-ax(celdas)) 
		det3=(cy(celdas)-ay(celdas))*(Cel_x-ax(celdas))
		det4=(Cel_y-ay(celdas))*(bx(celdas)-ax(celdas))
		coef2=det1*(bz-az)+det2*(cz-az)-det3*(bz-az)-det4*(cz-az)
		R1=max(az-coef2/coef1(celdas),0.0)		
		!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
		drenaid=N_cel-drena(1,celdas)+1	    
		!Al sistema le entra la lluvia
		entradas=entradas+R1
		!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial
		R2=max(0.0,R1-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
		E1=min(Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
		salidas=salidas+E1
		!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 
		R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
		Sp(2,celdas)=Sp(2,celdas)+R2-R3 ![mm] !Actualiza alm con la lluvia nueva
		Es2=E2(celdas)*Sp(2,celdas) ![mm] De acuerdo al almacenamiento calcula cuanto se va
		Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial
		R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		Sp(3,celdas)=Sp(3,celdas)+R3-R4 ![mm] servicioalcliente@flybox.com.co
		Es3=E3(celdas)*Sp(3,celdas) ![mm]
		Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial, nada precola		
		R5=min(R4,mm_kpp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
		Es4=E4(celdas)*Sp(4,celdas) ![mm]
		Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
		!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
		select case (tipo_celda(1,celdas))
		    case(1)
			!Sigue drenando a su tanque igual aguas abajo
			if (drena(1,celdas).ne.0) then
			    Sp(2,drenaid)=Sp(2,drenaid)+Es2
			    Sp(3,drenaid)=Sp(3,drenaid)+Es3
			    Sp(4,drenaid)=Sp(4,drenaid)+Es4
			else
			    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
			    salidas=salidas+Es2+Es3+Es4
			endif
		    case(2,3)			
			!El tanque 5 recibe agua de los tanques 2 y 3 fijo
			Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
			Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
			!Copia variables de vectores a escalares par aahorrar tiempo
			vel=v_cauce(celdas) ![m/seg]
			S5=Sp(5,celdas) ![mm]			
			L=L_celda(1,celdas) ![mts]
			pm=pend_man(celdas)
			!Calcula mediante onda cinematica el flujo a la salida
			do i=1,4
			    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
			    vn=(Area**(2/3))*pm ![m/seg]
			    vel=(2*vn+vel)/3 ![m2/seg]
			enddo
			v_cauce(celdas)=vel		            			
			Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
			Sp(5,celdas)=Sp(5,celdas)-Es5
			if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
		end select
		!si es la salida de la cuenca guarda
		if (drena(1,celdas).eq.0) then 		   
		    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    salidas=salidas+Es5 ![mm]
		endif
		!si es un punto de control guarda igualmente
		if (control(1,celdas).ne.0) then
		    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    control_cont=control_cont+1
		endif
		!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
		rain_sum=rain_sum+R1
	    enddo
	    !calcula cantidad total de lluvia que entra al sistema
	    entradas=entradas+rain_sum
	    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
	    mean_rain(tiempo)=rain_sum/N_cel
	enddo
	!Calcula y muestra el tiempo de ejecucion
	call etime(tiempo_ejec,tiempo_result)
	print *, 'Tiempo ejecucion: ', tiempo_result
    else
	print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
    endif
end subroutine

!model_interp_lk: Modelo shia completo, contiene: velocidad lineal en ladera 
!y velocidad cinematica en canal, no se usa la OCG. la lluvia es interpolada
!por idw. (no probado)
subroutine shia_idw_lk(calib,N_cel,N_cont,N_reg,Num_est,pp,Q,balance,mean_rain,sp)
    !Variables de entrada
    integer, intent(in) :: N_cel,N_reg,N_cont,Num_est
    real, intent(in) :: calib(9)
    real, intent(in) :: pp
    !Variables de salia
    real, intent(out) :: Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),balance
    !Variables locales 
    real tiempo_ejec(2),tiempo_result !variables de tiempo de ejecucion del programa
    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
    integer drenaid,Res !Vector con el id a donde drena cada celda
    real Rain,rain_sum,pot_local !campo de lluvia  para el intervalo de tiempo, potencial para idw local,
    character*3 corr !local de si se va a hacer correccion o no.
    real Hu_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
    real R1,R2,R3,R4,R5 !lluvia (R1) y flujo que drena por los tanques
    real v_ladera(nceldas),v_cauce(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
    real W(Num_est),Cel_x,Cel_y,Wr
    integer Cel_pert !Variables de interpolacion tin
    real m3_mm !Variable para convertir m3 a mm2
    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
    integer i,control_cont,cont !iterador,contador de puntos de control, contador de lluvia faltante    
    !Definiciones para f2py
    !f2py intent(in) :: N_cel,N_reg,N_cont,calib,Num_est,pp
    !f2py intent(out) :: Q,sp,mean_rain,balance
    !Preambulo a la ejecucion del modelo
    !Calcula la cantidad de agua que es retenida en el capilar
    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
    !Calcula las velocidades horizontales iniciales
    v_ladera=1.4*Calib(4)*(pend_celda(1,:)**0.5)/man(1,:) ![m/s] Vel ladera, Estado constante
    v_cauce=1 ![m/s] Vel ladera, Estado constante
    pend_man=(pend_celda(1,:)**(0.5))/man(1,:)
    ksh=ks(1,:)*Calib(6)*(conver_ks/1000)*pend_celda(1,:) ![m/s] Vel sub-superficial, Estado constante		
    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
    !Calcula el porcentaje de flujo horizontal saliente de cada celda
    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))
    !Convertor de mm a mt3 para obtener caudal a la salida
    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
    !Establece el almacenamiento inicial 
    Sp=S
    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
    inicial=sum(Sp(:,:))
    entradas=0
    salidas=0
    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
    mean_rain=0
    if (eval.eq.1) then
	!Calcula el tiempo inicial
	call etime(tiempo_ejec,tiempo_result)
	!Itera para cada intervalo de tiempo
	do tiempo=1,N_reg
	    !Reinicia el conteo de la lluvia y el contador de los puntos de control
	    rain_sum=0
	    control_cont=2	    	    
	    !Itera para todas las celdas
	    do celdas=1,N_cel
		!Interpola la lluvia
		Cel_x=x(1,celdas) ; Cel_y=y(1,celdas)
		do i=1,Num_est
		    W(i)=1.0/(sqrt(((coord(1,i)-Cel_x)**2+(coord(2,i)-Cel_y)**2)))**pp
		end do
		Wr=sum(W*lluvia(:,tiempo),mask=lluvia(:,tiempo).gt.0.0)
		R1=Wr/sum(W,mask=lluvia(:,tiempo).ge.0.0)
		!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
		drenaid=N_cel-drena(1,celdas)+1	    
		!Al sistema le entra la lluvia
		entradas=entradas+R1
		!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial
		R2=max(0.0,R1-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
		E1=min(Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
		salidas=salidas+E1
		!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 
		R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
		Sp(2,celdas)=Sp(2,celdas)+R2-R3 ![mm] !Actualiza alm con la lluvia nueva
		Es2=E2(celdas)*Sp(2,celdas) ![mm] De acuerdo al almacenamiento calcula cuanto se va
		Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial
		R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		Sp(3,celdas)=Sp(3,celdas)+R3-R4 ![mm] servicioalcliente@flybox.com.co
		Es3=E3(celdas)*Sp(3,celdas) ![mm]
		Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial, nada precola		
		R5=min(R4,mm_kpp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
		Es4=E4(celdas)*Sp(4,celdas) ![mm]
		Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
		!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
		select case (tipo_celda(1,celdas))
		    case(1)
			!Sigue drenando a su tanque igual aguas abajo
			if (drena(1,celdas).ne.0) then
			    Sp(2,drenaid)=Sp(2,drenaid)+Es2
			    Sp(3,drenaid)=Sp(3,drenaid)+Es3
			    Sp(4,drenaid)=Sp(4,drenaid)+Es4
			else
			    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
			    salidas=salidas+Es2+Es3+Es4
			endif
		    case(2,3)			
			!El tanque 5 recibe agua de los tanques 2 y 3 fijo
			Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
			Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
			!Copia variables de vectores a escalares par ahorrar tiempo
			vel=v_cauce(celdas) ![m/seg]
			S5=Sp(5,celdas) ![mm]			
			L=L_celda(1,celdas) ![mts]
			pm=pend_man(celdas)
			!Calcula mediante onda cinematica el flujo a la salida
			do i=1,4
			    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
			    vn=(Area**(2/3))*pm ![m/seg]
			    vel=(2*vn+vel)/3 ![m2/seg]
			enddo
			v_cauce(celdas)=vel		            			
			Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
			Sp(5,celdas)=Sp(5,celdas)-Es5
			if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
		end select
		!si es la salida de la cuenca guarda
		if (drena(1,celdas).eq.0) then 		   
		    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    salidas=salidas+Es5 ![mm]
		endif
		!si es un punto de control guarda igualmente
		if (control(1,celdas).ne.0) then
		    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    control_cont=control_cont+1
		endif
		!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
		rain_sum=rain_sum+R1
	    enddo
	    !calcula cantidad total de lluvia que entra al sistema
	    entradas=entradas+rain_sum
	    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
	    mean_rain(tiempo)=rain_sum/N_cel
	enddo
	!Calcula y muestra el tiempo de ejecucion
	call etime(tiempo_ejec,tiempo_result)
	print *, 'Tiempo ejecucion: ', tiempo_result
    else
	print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
    endif
end subroutine

!model_idw_klk: Modelo shia completo, contiene: velocidad lineal en ladera,
!velociad no lineal sub-superficial, velocidad cinematica en canal, no se usa la OCG. 
!la lluvia es interpolada por idw. (no probado)
subroutine shia_idw_klk(calib,N_cel,N_cont,N_contH,N_reg,Num_est,pp,Q,Hum,Etr,Infiltra,mean_rain,sp)
    !Variables de entrada
    integer, intent(in) :: N_cel,N_reg,N_cont,Num_est,N_contH
    real, intent(in) :: calib(10)
    real, intent(in) :: pp
    !Variables de salia
    real, intent(out) :: Hum(N_contH,N_reg),Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),Etr(N_contH,N_reg)
    real, intent(out) :: Infiltra(N_contH,N_reg)
    !Variables locales 
    real tiempo_ejec(2),tiempo_result !variables de tiempo de ejecucion del programa
    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
    integer drenaid,Res !Vector con el id a donde drena cada celda
    real Rain,rain_sum,pot_local !campo de lluvia  para el intervalo de tiempo, potencial para idw local,
    character*3 corr !local de si se va a hacer correccion o no.
    real Hu_loc(nceldas),H3_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
    real R1,R2,R3,R4,R5,Z3 !lluvia (R1) y flujo que drena por los tanques, y retorno del tanque 3
    real v_ladera(nceldas),v_cauce(nceldas),v_sub(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
    real W(Num_est),Cel_x,Cel_y,Wr
    integer Cel_pert !Variables de interpolacion tin
    real m3_mm !Variable para convertir m3 a mm2
    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
    integer i,control_cont,cont_h,cont !iterador,contador de puntos de control, contador de lluvia faltante    
    !Definiciones para f2py
    !f2py intent(in) :: N_cel,N_reg,N_cont,calib,Num_est,pp,N_contH
    !f2py intent(out) :: Q,Hum,sp,mean_rain,Etr,Infiltra
    !Preambulo a la ejecucion del modelo
    !Convertor de mm a mt3 para obtener caudal a la salida    
    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
    !Calcula la cantidad de agua que es retenida en el capilar
    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
    H3_loc=H3(1,:)*Calib(10) !Cantidad de agua que es almacenada gravitacionalmente
    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
    !Calcula las velocidades horizontales iniciales
    v_ladera=1.4*Calib(4)*(pend_celda(1,:)**0.5)/man(1,:) ![m/s] Vel ladera, Estado constante
    v_cauce=1; v_sub=0.1 ![m/s] Vel inicial cauce, Vel inicial sub-superficial
    pend_man=(pend_celda(1,:)**(0.5))/man(1,:)
    ksh=ks(1,:)*(conver_ks/1000) ![m/s] Convierte la velosidad de unidades		    
    ksh=(Calib(6)*ksh*pend_celda(1,:)*dxP**2)/(3*(H3_loc*m3_mm)**2) !Expresion constante de kubota y Sivapalan, 1995        
    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
    !Calcula el porcentaje de flujo horizontal saliente de cada celda
    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))    
    !Establece el almacenamiento inicial 
    Sp=S
    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
    inicial=sum(Sp(:,:))
    entradas=0
    salidas=0
    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
    mean_rain=0 
    if (eval.eq.1) then
	!Calcula el tiempo inicial
	call etime(tiempo_ejec,tiempo_result)
	!Itera para cada intervalo de tiempo
	do tiempo=1,N_reg
	    !Reinicia el conteo de la lluvia y el contador de los puntos de control
	    rain_sum=0
	    control_cont=2	    	    
	    cont_h=0
	    !Itera para todas las celdas
	    do celdas=1,N_cel
		!Interpola la lluvia		
		Cel_x=x(1,celdas) ; Cel_y=y(1,celdas)		
		do i=1,Num_est
		    W(i)=1.0/(sqrt(((coord(1,i)-Cel_x)**2+(coord(2,i)-Cel_y)**2)))**pp
		end do		
		Wr=sum(W*lluvia(:,tiempo),mask=lluvia(:,tiempo).gt.0.0)
		R1=Wr/sum(W,mask=lluvia(:,tiempo).ge.0.0)		
		!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
		drenaid=N_cel-drena(1,celdas)+1	    
		!Al sistema le entra la lluvia
		entradas=entradas+R1				
		!Flujo vertical entre tanques		
		R2=max(0.0,R1-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
		R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
		R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		R5=min(R4,mm_kpp(celdas)) !pierde el minimo entre lo que hay y la conductividad del acuifero				
		!Determina si hay o no retorno del tanque 3 
		Z3=max(0.0,Sp(3,celdas)+R3-R4-H3_loc(celdas))	    		   
		!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial				
		Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
		E1=min(evp_p(1,tiempo)*Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
		salidas=salidas+E1		
		!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 			    
		Sp(2,celdas)=Sp(2,celdas)+R2+Z3-R3 ![mm] !Actualiza alm con la lluvia nueva
		Es2=E2(celdas)*Sp(2,celdas) ![mm] De acuerdo al almacenamiento calcula cuanto se va
		Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         		
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial		
		Sp(3,celdas)=Sp(3,celdas)+R3-Z3-R4 ![mm] 
		pm=ksh(celdas); vel=v_sub(celdas) !Copia variables por velocidad
		do i=1,4
		    Area=Sp(3,celdas)*m3_mm/(dxp+vel*dt) ![m2] Calcula el area de la seccion
		    vn=pm*(Area**2) ![m/seg] Calcula la velocidad nueva
		    vel=(2*vn+vel)/3.0 ![m/seg] Promedia la velocidad
		enddo		
		v_sub(celdas)=vel ![m/seg]
		Es3=Area*vel*dt/m3_mm ![mm]		
		Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
		if (control_h(1,celdas).ne.0) then
		    cont_h=cont_h+1
		    Hum(cont_h,tiempo)=(Sp(3,celdas)+Sp(1,celdas))/(Hu_loc(celdas)+H3_loc(celdas))
		    Etr(cont_h,tiempo)=E1
		    Infiltra(cont_h,tiempo)=R3
		endif		
		!Tanque 4: Calculo de la cantidad de agua que escurre como flujo subterraneo
		Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
		Es4=E4(celdas)*Sp(4,celdas) ![mm]
		Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
		!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
		select case (tipo_celda(1,celdas))
		    case(1)
			!Sigue drenando a su tanque igual aguas abajo
			if (drena(1,celdas).ne.0) then
			    Sp(2,drenaid)=Sp(2,drenaid)+Es2
			    Sp(3,drenaid)=Sp(3,drenaid)+Es3
			    Sp(4,drenaid)=Sp(4,drenaid)+Es4
			else
			    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
			    salidas=salidas+Es2+Es3+Es4
			endif
		    case(2,3)			
			!El tanque 5 recibe agua de los tanques 2 y 3 fijo
			Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
			Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
			!Copia variables de vectores a escalares par ahorrar tiempo
			vel=v_cauce(celdas) ![m/seg]
			S5=Sp(5,celdas) ![mm]			
			L=L_celda(1,celdas) ![mts]
			pm=pend_man(celdas)
			!Calcula mediante onda cinematica el flujo a la salida
			do i=1,4
			    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
			    vn=(Area**(2/3))*pm ![m/seg]
			    vel=(2*vn+vel)/3 ![m2/seg]
			enddo
			v_cauce(celdas)=vel		            			
			Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
			Sp(5,celdas)=Sp(5,celdas)-Es5
			if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
		end select		
		!si es la salida de la cuenca guarda
		if (drena(1,celdas).eq.0) then 		   
		    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    salidas=salidas+Es5 ![mm]
		endif		
		!si es un punto de control guarda igualmente		
		if (control(1,celdas).ne.0) then
		    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    control_cont=control_cont+1
		endif		
		!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
		rain_sum=rain_sum+R1
	    enddo
	    !calcula cantidad total de lluvia que entra al sistema	    
	    entradas=entradas+rain_sum
	    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
	    mean_rain(tiempo)=rain_sum/N_cel	   
	enddo
	!Calcula y muestra el tiempo de ejecucion
	call etime(tiempo_ejec,tiempo_result)
	print *, 'Tiempo ejecucion: ', tiempo_result
    else
	print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
    endif
end subroutine

!model_idw_kkk: Modelo shia completo, contiene: velocidad no lineal en ladera,
!velociad no lineal sub-superficial, velocidad cinematica en canal, no se usa la OCG. 
!la lluvia es interpolada por idw. (no probado)
subroutine shia_idw_kkk(calib,N_cel,N_cont,N_contH,N_reg,Num_est,pp,Q,Hum,balance,mean_rain,sp)
    !Variables de entrada
    integer, intent(in) :: N_cel,N_reg,N_cont,Num_est,N_contH
    real, intent(in) :: calib(10)
    real, intent(in) :: pp
    !Variables de salia
    real, intent(out) :: Hum(N_contH,N_reg),Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),balance
    !Variables locales 
    real tiempo_ejec(2),tiempo_result !variables de tiempo de ejecucion del programa
    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
    integer drenaid,Res !Vector con el id a donde drena cada celda
    real Rain,rain_sum,pot_local !campo de lluvia  para el intervalo de tiempo, potencial para idw local,
    character*3 corr !local de si se va a hacer correccion o no.
    real Hu_loc(nceldas),H3_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
    real R1,R2,R3,R4,R5,Z3 !lluvia (R1) y flujo que drena por los tanques, y retorno del tanque 3
    real v_ladera(nceldas),v_cauce(nceldas),v_sub(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
    real pend_man_lad(nceldas) !combinacion pendiente manning y coeficientes para flujo en laderas
    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
    real W(Num_est),Cel_x,Cel_y,Wr
    integer Cel_pert !Variables de interpolacion tin
    real m3_mm !Variable para convertir m3 a mm2
    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
    integer i,control_cont,cont_h,cont !iterador,contador de puntos de control, contador de lluvia faltante    
    !Definiciones para f2py
    !f2py intent(in) :: N_cel,N_reg,N_cont,calib,Num_est,pp,N_contH
    !f2py intent(out) :: Q,Hum,sp,mean_rain,balance
    !Preambulo a la ejecucion del modelo
    !Convertor de mm a mt3 para obtener caudal a la salida    
    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
    !Calcula la cantidad de agua que es retenida en el capilar
    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
    H3_loc=H3(1,:)*Calib(10) !Cantidad de agua que es almacenada gravitacionalmente
    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
    !Calcula las velocidades horizontales iniciales
    v_ladera=0.5 ![m/s] Vel ladera, Estado constante
    v_cauce=1; v_sub=0.1 ![m/s] Vel inicial cauce, Vel inicial sub-superficial
    pend_man=(pend_celda(1,:)**(0.5))/man(1,:) !combinacion pend y manning para flujo en cauce
    pend_man_lad=Calib(4)*(epsilo/man(1,:))*(pend_celda(1,:)**0.5)
    ksh=ks(1,:)*(conver_ks/1000) ![m/s] Convierte la velosidad de unidades		    
    ksh=(Calib(6)*ksh*pend_celda(1,:)*dxP**2)/(3*(H3_loc*m3_mm)**2) !Expresion constante de kubota y Sivapalan, 1995        
    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
    !Calcula el porcentaje de flujo horizontal saliente de cada celda
    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))    
    !Establece el almacenamiento inicial 
    Sp=S
    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
    inicial=sum(Sp(:,:))
    entradas=0
    salidas=0
    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
    mean_rain=0 
    if (eval.eq.1) then
	!Calcula el tiempo inicial
	call etime(tiempo_ejec,tiempo_result)
	!Itera para cada intervalo de tiempo
	do tiempo=1,N_reg
	    !Reinicia el conteo de la lluvia y el contador de los puntos de control
	    rain_sum=0
	    control_cont=2	    	    
	    cont_h=0
	    !Itera para todas las celdas
	    do celdas=1,N_cel
		!Interpola la lluvia		
		Cel_x=x(1,celdas) ; Cel_y=y(1,celdas)		
		do i=1,Num_est
		    W(i)=1.0/(sqrt(((coord(1,i)-Cel_x)**2+(coord(2,i)-Cel_y)**2)))**pp
		end do		
		Wr=sum(W*lluvia(:,tiempo),mask=lluvia(:,tiempo).gt.0.0)
		R1=Wr/sum(W,mask=lluvia(:,tiempo).ge.0.0)		
		!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
		drenaid=N_cel-drena(1,celdas)+1	    
		!Al sistema le entra la lluvia
		entradas=entradas+R1				
		!Flujo vertical entre tanques		
		R2=max(0.0,R1-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
		R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
		R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
		R5=min(R4,mm_kpp(celdas)) !pierde el minimo entre lo que hay y la conductividad del acuifero				
		!Determina si hay o no retorno del tanque 3 
		Z3=max(0.0,Sp(3,celdas)+R3-R4-H3_loc(celdas))	    		   
		!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial				
		Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
		E1=min(evp_p(1,tiempo)*Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
		Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
		salidas=salidas+E1		
		!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 			    
		Sp(2,celdas)=Sp(2,celdas)+R2+Z3-R3 ![mm] !Actualiza alm con la lluvia nueva
		pm=pend_man_lad(celdas); vel=v_ladera(celdas)
		do i=1,4
		    Area=Sp(2,celdas)*m3_mm/(dxp+vel*dt) ![m2] Calcula el area de la seccion
		    vn=pm*(Area**2) ![m/seg] Calcula la velocidad nueva
		    vel=(2*vn+vel)/3.0 ![m/seg] Promedia la velocidad
		enddo
		v_ladera(celdas)=vel ![m/seg]
		Es2=Area*vel*dt/m3_mm ![mm]		
		Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         		
		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial		
		Sp(3,celdas)=Sp(3,celdas)+R3-Z3-R4 ![mm] 
		pm=ksh(celdas); vel=v_sub(celdas) !Copia variables por velocidad
		do i=1,4
		    Area=Sp(3,celdas)*m3_mm/(dxp+vel*dt) ![m2] Calcula el area de la seccion
		    vn=pm*(Area**2) ![m/seg] Calcula la velocidad nueva
		    vel=(2*vn+vel)/3.0 ![m/seg] Promedia la velocidad
		enddo		
		v_sub(celdas)=vel ![m/seg]
		Es3=Area*vel*dt/m3_mm ![mm]		
		Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
		if (control_h(1,celdas).ne.0) then
		    cont_h=cont_h+1
		    Hum(cont_h,tiempo)=Sp(3,celdas)+Sp(1,celdas)
		endif		
		!Tanque 4: Calculo de la cantidad de agua que escurre como flujo subterraneo
		Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
		Es4=E4(celdas)*Sp(4,celdas) ![mm]
		Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
		!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
		select case (tipo_celda(1,celdas))
		    case(1)
			!Sigue drenando a su tanque igual aguas abajo
			if (drena(1,celdas).ne.0) then
			    Sp(2,drenaid)=Sp(2,drenaid)+Es2
			    Sp(3,drenaid)=Sp(3,drenaid)+Es3
			    Sp(4,drenaid)=Sp(4,drenaid)+Es4
			else
			    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
			    salidas=salidas+Es2+Es3+Es4
			endif
		    case(2,3)			
			!El tanque 5 recibe agua de los tanques 2 y 3 fijo
			Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
			Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
			!Copia variables de vectores a escalares par ahorrar tiempo
			vel=v_cauce(celdas) ![m/seg]
			S5=Sp(5,celdas) ![mm]			
			L=L_celda(1,celdas) ![mts]
			pm=pend_man(celdas)
			!Calcula mediante onda cinematica el flujo a la salida
			do i=1,4
			    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
			    vn=(Area**(2/3))*pm ![m/seg]
			    vel=(2*vn+vel)/3 ![m2/seg]
			enddo
			v_cauce(celdas)=vel		            			
			Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
			Sp(5,celdas)=Sp(5,celdas)-Es5
			if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
		end select		
		!si es la salida de la cuenca guarda
		if (drena(1,celdas).eq.0) then 		   
		    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    salidas=salidas+Es5 ![mm]
		endif		
		!si es un punto de control guarda igualmente		
		if (control(1,celdas).ne.0) then
		    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
		    control_cont=control_cont+1
		endif		
		!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
		rain_sum=rain_sum+R1
	    enddo
	    !calcula cantidad total de lluvia que entra al sistema	    
	    entradas=entradas+rain_sum
	    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
	    mean_rain(tiempo)=rain_sum/N_cel	   
	enddo
	!Calcula y muestra el tiempo de ejecucion
	call etime(tiempo_ejec,tiempo_result)
	print *, 'Tiempo ejecucion: ', tiempo_result
    else
	print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
    endif
end subroutine

!model_interp_lk: Modelo shia completo, contiene: velocidad lineal en ladera 
!y velocidad cinematica en canal, no se usa la OCG. la lluvia es interpolada
!por idw o tin de acuerdo a lo indicado.
!subroutine shia_interp_lk(calib,tipo,N_cel,N_cont,N_reg,corr_sino,pot,Q,balance,mean_rain,sp)
!    !Variables de entrada
!    integer, intent(in) :: N_cel,N_reg,N_cont
!    real, intent(in) :: calib(9)
!    real, intent(in), optional :: pot
!    character*3, intent(in) :: tipo
!    character*3, intent(in), optional :: corr_sino
!    !Variables de salia
!    real, intent(out) :: Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),balance
!    !Variables locales 
!    real tiempo_i,tiempo_f !variables de tiempo de ejecucion del programa
!    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
!    integer drenaid,Res !Vector con el id a donde drena cada celda
!    real Rain(nceldas),rain_sum,pot_local !campo de lluvia  para el intervalo de tiempo, potencial para idw local,
!    character*3 corr !local de si se va a hacer correccion o no.
!    real Hu_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
!    real R1,R2,R3,R4,R5 !lluvia (R1) y flujo que drena por los tanques
!    real v_ladera(nceldas),v_cauce(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
!    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
!    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
!    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
!    real m3_mm !Variable para convertir m3 a mm2
!    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
!    integer i,control_cont,cont !iterador,contador de puntos de control, contador de lluvia faltante
!    !Definiciones para f2py
!    !f2py intent(in) :: N_cel,N_reg,N_cont,calib,tipo
!    !f2py intent(in), optional :: pot
!    !f2py intent(out) :: Q,sp,mean_rain,balance
!    !Preambulo a la ejecucion del modelo
!    !Calcula la cantidad de agua que es retenida en el capilar
!    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
!    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
!    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
!    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
!    !Calcula las velocidades horizontales iniciales
!    v_ladera=1.4*Calib(4)*(pend_celda(1,:)**0.5)/man(1,:) ![m/s] Vel ladera, Estado constante
!    v_cauce=1 ![m/s] Vel ladera, Estado constante
!    pend_man=(pend_celda(1,:)**(0.5))/man(1,:)
!    ksh=ks(1,:)*Calib(6)*(conver_ks/1000)*pend_celda(1,:) ![m/s] Vel sub-superficial, Estado constante		
!    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
!    !Calcula el porcentaje de flujo horizontal saliente de cada celda
!    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
!    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
!    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
!    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))
!    !Convertor de mm a mt3 para obtener caudal a la salida
!    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
!    !Establece el almacenamiento inicial 
!    Sp=S
!    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
!    inicial=sum(Sp(:,:))
!    entradas=0
!    salidas=0
!    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
!    mean_rain=0
!    !Si se va a interpolar con idw verifica el potencial a usar
!    if (tipo.eq.'idw') then
!	if (present(pot)) then
!	    if (pot.lt.1.0) then
!		pot_local=1.0
!	    else
!		pot_local=pot
!	    endif
!	else
!	    pot_local=1.0
!	endif
!    elseif (tipo.eq.'tin') then
!	pot_local=1.0
!    else
!	eval=0
!    endif
!    !Verifica si van a hacer correcciones o no
!	if (present(corr_sino)) then
!	    if (len_trim(corr_sino).gt.0) then
!			corr=corr_sino
!	    else
!			corr='no'
!	    endif
!	endif
!    if (eval.eq.1) then
!		!Itera para cada intervalo de tiempo
!		do tiempo=1,N_reg
!		    !Reinicia el conteo de la lluvia y el contador de los puntos de control
!		    rain_sum=0
!		    control_cont=2
!		    !interpola la lluvia para todas las celdas en el intervalo de tiempo
!		    if (tipo.eq.'tin') then
!				call interpolation_tin_one(Rain,x,y,tiempo,nceldas,correccion=corr_sino)
!		    elseif (tipo.eq.'idw') then
!				call interpolation_idw_one(Rain,x,y,tiempo,nceldas,pp=pot_local,correccion=corr_sino)
!		    endif		    
!		    !Itera para todas las celdas
!		    do celdas=1,N_cel
!				!Verifica la lluvia
!				if (Rain(celdas).lt.0 .or. Rain(celdas).eq.0) then
!				    R1=0.0
!				else
!				    R1=Rain(celdas)
!				endif
!				!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
!				drenaid=N_cel-drena(1,celdas)+1	    
!				!Al sistema le entra la lluvia
!				entradas=entradas+R1
!				!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial
!				R2=max(0.0,Rain(celdas)-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
!				Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
!				E1=min(Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
!				Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
!				salidas=salidas+E1
!				!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 
!				R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
!				Sp(2,celdas)=Sp(2,celdas)+R2-R3 ![mm] !Actualiza alm con la lluvia nueva
!				Es2=E2(celdas)*Sp(2,celdas) ![mm] De acuerdo al almacenamiento calcula cuanto se va
!				Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         
!				!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial
!				R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
!				Sp(3,celdas)=Sp(3,celdas)+R3-R4 ![mm] servicioalcliente@flybox.com.co
!				Es3=E3(celdas)*Sp(3,celdas) ![mm]
!				Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
!				!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial, nada precola		
!				R5=min(R4,mm_kpp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
!				Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
!				Es4=E4(celdas)*Sp(4,celdas) ![mm]
!				Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
!				!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
!				select case (tipo_celda(1,celdas))
!				    case(1)
!					!Sigue drenando a su tanque igual aguas abajo
!					if (drena(1,celdas).ne.0) then
!					    Sp(2,drenaid)=Sp(2,drenaid)+Es2
!					    Sp(3,drenaid)=Sp(3,drenaid)+Es3
!					    Sp(4,drenaid)=Sp(4,drenaid)+Es4
!					else
!					    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
!					    salidas=salidas+Es2+Es3+Es4
!					endif
!				    case(2,3)			
!					!El tanque 5 recibe agua de los tanques 2 y 3 fijo
!					Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
!					Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
!					!Copia variables de vectores a escalares par aahorrar tiempo
!					vel=v_cauce(celdas) ![m/seg]
!					S5=Sp(5,celdas) ![mm]			
!					L=L_celda(1,celdas) ![mts]
!					pm=pend_man(celdas)
!					!Calcula mediante onda cinematica el flujo a la salida
!					do i=1,4
!					    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
!					    vn=(Area**(2/3))*pm ![m/seg]
!					    vel=(2*vn+vel)/3 ![m2/seg]
!					enddo
!					v_cauce(celdas)=vel		            			
!					Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
!					Sp(5,celdas)=Sp(5,celdas)-Es5
!					if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
!				end select
!				!si es la salida de la cuenca guarda
!				if (drena(1,celdas).eq.0) then 		   
!				    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
!				    salidas=salidas+Es5 ![mm]
!				endif
!				!si es un punto de control guarda igualmente
!				if (control(1,celdas).ne.0) then
!				    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
!				    control_cont=control_cont+1
!				endif
!				!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
!				rain_sum=rain_sum+R1
!		    enddo
!		    !calcula cantidad total de lluvia que entra al sistema
!		    entradas=entradas+rain_sum
!		    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
!		    mean_rain(tiempo)=rain_sum/N_cel
!		enddo
!    else
!		print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
!    endif
!end subroutine

!model_field_lk: Modelo shia completo, contiene: velocidad lineal en ladera 
!y velocidad cinematica en canal, no se usa la OCG. lluvia es leida por 
!archivo, generado por ll.interpolation_idw o ll.interpolation_tin, o radar
!con el mismo formato.
!subroutine shia_field_lk(calib,ruta_rain,N_cel,N_cont,N_reg,Q,balance,mean_rain,sp)
!    !Variables de entrada
!    integer, intent(in) :: N_cel,N_reg,N_cont
!    real, intent(in) :: calib(9)
!    character*255, intent(in) :: ruta_rain
!    !Variables de salia
!    real, intent(out) :: Q(N_cont,N_reg),sp(5,N_cel),mean_rain(N_reg),balance
!    !Variables locales 
!    real tiempo_i,tiempo_f !variables de tiempo de ejecucion del programa
!    integer celdas,tiempo !Iteradores para la cantidad de celdas y los intervalos de tiempo
!    integer drenaid,Res !Vector con el id a donde drena cada celda
!    real Rain(nceldas),rain_sum !campo de lluvia  para el intervalo de tiempo
!    real Hu_loc(nceldas) !Hu Local es una copia de Hu multiplicada por la claibracion [mm]
!    real R1,R2,R3,R4,R5 !lluvia (R1) y flujo que drena por los tanques
!    real v_ladera(nceldas),v_cauce(nceldas),ksh(nceldas),kph(nceldas) !velocidad en ladera, Velocidad del flujo sub-superficial horizontal
!    real pend_man(nceldas), pm, L, Area, vel, vn, S5 !combinado pendiente manning para calcular, Long, Area y velocidad para calcular flujo cinematico 
!    real mm_ks(nceldas),mm_kp(nceldas),mm_kpp(nceldas) !Velocidad de la conductividad vertical
!    real E2(nceldas),E3(nceldas),E4(nceldas),E5(nceldas),Es2,Es3,Es4,Es5,E1 !Cantidad de flujo que viaja en cada celda, cantidad de flujo que sale sub-superficial, Cantidad de flujo evaporado de la celda
!    real m3_mm !Variable para convertir m3 a mm2
!    real inicial,entradas,salidas !Cantidad de agua inicial, que entra al sistema y que sale [mm]
!    real X,Y !Posiciones actuales de la celda
!    integer i,control_cont,cont !iterador,contador de puntos de control, contador de lluvia faltante
!    !Definiciones para f2py
!    !f2py intent(in) :: N_cel,N_reg,N_cont,calib
!    !f2py intent(out) :: Q,sp,mean_rain,balance
!    !Preambulo a la ejecucion del modelo
!    !Calcula el tiempo inicial
!    call cpu_time(tiempo_i)
!    !Calcula la cantidad de agua que es retenida en el capilar
!    Hu_loc=Hu(1,:)*Calib(1) !Cantidad de agua almacenada en el suelo antes de escurrir
!    mm_ks=ks(1,:)*Calib(3)*dt*conver_ks ![mm] Velocidad a la que infiltra el agua
!    mm_kp=kp(1,:)*Calib(5)*dt*conver_kp ![mm] Velocidad a la que precola el agua
!    mm_kpp=kp(1,:)*Calib(7)*dt*conver_kp ![mm] Velocidad a la que se dan perdidas de agua
!    !Calcula las velocidades horizontales iniciales
!    v_ladera=1.4*Calib(4)*(pend_celda(1,:)**0.5)/man(1,:) ![m/s] Vel ladera, Estado constante
!    v_cauce=1 ![m/s] Vel ladera, Estado constante
!    pend_man=(pend_celda(1,:)**(0.5))/man(1,:)
!    ksh=ks(1,:)*Calib(6)*(conver_ks/1000)*pend_celda(1,:) ![m/s] Vel sub-superficial, Estado constante		
!    kph=kp(1,:)*Calib(8)*(conver_kp/1000)*pend_celda(1,:) ![m/s] Vel acuifero, Estado constante		
!    !Calcula el porcentaje de flujo horizontal saliente de cada celda
!    E2=1-L_celda(1,:)/(v_ladera*dt+L_celda(1,:))
!    E3=1-L_celda(1,:)/(ksh*dt+L_celda(1,:))
!    E4=1-L_celda(1,:)/(kph*dt+L_celda(1,:))
!    E5=1-L_celda(1,:)/(v_cauce*dt+L_celda(1,:))
!    !Convertor de mm a mt3 para obtener caudal a la salida
!    m3_mm=(dxp**2)/1000 ![m2 * 1m/1000mm] --> [m3/mm] convierte tanque S5[mm] a [m3]
!    !Establece el almacenamiento inicial 
!    Sp=S
!    !Establece la cantidad de agua inicial dentro del sistema y la cantidad de salida y de entrada
!    inicial=sum(Sp(:,:))
!    entradas=0
!    salidas=0
!    !Determina como lluvia anterior y la lluvia media para cada celda el valor cero
!    mean_rain=0
!    if (eval.eq.1) then
!	!Itera para cada intervalo de tiempo
!	do tiempo=1,N_reg
!	    !Reinicia el conteo de la lluvia y el contador de los puntos de control
!	    rain_sum=0
!	    control_cont=2
!	    !lee la lluvia para el intervalo
!	    call read_float_basin(ruta_rain,tiempo,Rain,res,1,N_cel)   
!	    !Itera para todas las celdas
!	    do celdas=1,N_cel
!		!Verifica la lluvia
!		if (Rain(celdas).lt.0 .or. Rain(celdas).eq.0) then
!		    R1=0.0
!		else
!		    R1=Rain(celdas)
!		endif
!		!Calcula la posicion de la celda objetivo y copia la posicion X,Y de la celda actual
!		drenaid=N_cel-drena(1,celdas)+1	    
!		!Al sistema le entra la lluvia
!		entradas=entradas+R1
!		!Tanque 1: Calculo de la cantidad de agua que es evaporada y la sobrante que pasa al flujo superficial
!		R2=max(0.0,Rain(celdas)-Hu_loc(celdas)+Sp(1,celdas)) ![mm]
!		Sp(1,celdas)=Sp(1,celdas)+R1-R2 ![mm] 
!		E1=min(Evp(1,celdas)*Calib(2)*(Sp(1,celdas)/Hu_loc(celdas))**0.6,Sp(1,celdas)) ![mm]
!		Sp(1,celdas)=Sp(1,celdas)-E1 ![mm]
!		salidas=salidas+E1
!		!Tanque 2: Flujo superficial, lo que no queda atrapado en capilar fluye 
!		R3=min(R2,mm_ks(celdas)) !Infiltra el minimo entre lo que hay y la conductividad 		
!		Sp(2,celdas)=Sp(2,celdas)+R2-R3 ![mm] !Actualiza alm con la lluvia nueva
!		Es2=E2(celdas)*Sp(2,celdas) ![mm] De acuerdo al almacenamiento calcula cuanto se va
!		Sp(2,celdas)=Sp(2,celdas)-Es2 ![mm] Actualiza almacenamiento         
!		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial
!		R4=min(R3,mm_kp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
!		Sp(3,celdas)=Sp(3,celdas)+R3-R4 ![mm] 
!		Es3=E3(celdas)*Sp(3,celdas) ![mm]
!		Sp(3,celdas)=Sp(3,celdas)-Es3 ![mm]	     			    
!		!Tanque 3: Calculo de la cantidad de agua que escurre como flujo sub-superficial, nada precola		
!		R5=min(R4,mm_kpp(celdas)) !precola el minimo entre lo que hay y la conductividad del acuifero		
!		Sp(4,celdas)=Sp(4,celdas)+R4-R5 ![mm]
!		Es4=E4(celdas)*Sp(4,celdas) ![mm]
!		Sp(4,celdas)=Sp(4,celdas)-Es4 ![mm]	     			    		
!		!Selecciona a donde enviar el flujo de acuerdo al tipo de celda
!		select case (tipo_celda(1,celdas))
!		    case(1)
!			!Sigue drenando a su tanque igual aguas abajo
!			if (drena(1,celdas).ne.0) then
!			    Sp(2,drenaid)=Sp(2,drenaid)+Es2
!			    Sp(3,drenaid)=Sp(3,drenaid)+Es3
!			    Sp(4,drenaid)=Sp(4,drenaid)+Es4
!			else
!			    Q(1,tiempo)=Es2*m3_mm/dt ![m3/s]
!			    salidas=salidas+Es2+Es3+Es4
!			endif
!		    case(2,3)			
!			!El tanque 5 recibe agua de los tanques 2 y 3 fijo
!			Sp(5,celdas)=Sp(5,celdas)+Es2+Es3+Es4*(tipo_celda(1,celdas)-2) ![mm]
!			Sp(4,drenaid)=Sp(4,drenaid)+Es4*(3-tipo_celda(1,celdas)) ![mm]
!			!Copia variables de vectores a escalares par aahorrar tiempo
!			vel=v_cauce(celdas) ![m/seg]
!			S5=Sp(5,celdas) ![mm]			
!			L=L_celda(1,celdas) ![mts]
!			pm=pend_man(celdas)
!			!Calcula mediante onda cinematica el flujo a la salida
!			do i=1,4
!			    Area=Sp(5,celdas)*m3_mm/(L+vel*dt) ![m2]
!			    vn=(Area**(2/3))*pm ![m/seg]
!			    vel=(2*vn+vel)/3 ![m2/seg]
!			enddo
!			v_cauce(celdas)=vel		            			
!			Es5=min(Area*v_cauce(celdas)*dt*Calib(9)/m3_mm,Sp(5,celdas))
!			Sp(5,celdas)=Sp(5,celdas)-Es5
!			if (drena(1,celdas).ne.0) Sp(5,drenaid)=Sp(5,drenaid)+Es5	![mm]			
!		end select
!		!si es la salida de la cuenca guarda
!		if (drena(1,celdas).eq.0) then 		   
!		    Q(1,tiempo)=Es5*m3_mm/dt ![m3/s]      
!		    salidas=salidas+Es5 ![mm]
!		endif
!		!si es un punto de control guarda igualmente
!		if (control(1,celdas).ne.0) then
!		    Q(control_cont,tiempo)=Es5*m3_mm/dt ![m3/s]      
!		    control_cont=control_cont+1
!		endif
!		!Lluvia media: suma la cantidad de lluvia que cae sobre la cuenca 
!		rain_sum=rain_sum+R1
!	    enddo
!	    !calcula cantidad total de lluvia que entra al sistema
!	    entradas=entradas+rain_sum
!	    !Calculo de la lluvia media sobre la cuenca en el intervalo de tiempo
!	    mean_rain(tiempo)=rain_sum/N_cel
!	enddo
!    else
!	print *, 'Aviso: El modelo no ha ejecutado faltan variables por asignar dimension!!!'
!    endif
!end subroutine

end module

!-----------------------------------------------------------------------
!Subrutinas extras del moduo que son usadas internamente por modelos
!-----------------------------------------------------------------------

!Lee los datos flotantes de un binario de cuenca en los records ordenados
subroutine read_float_basin(ruta,records,vect,Res,nrecords,nceldas) 
    !Variables de entrada
    integer, intent(in) :: nrecords,nceldas
    character*255, intent(in) :: ruta
    integer, intent(in) :: records(nrecords)
    !Variables de salida
    real, intent(out) :: vect(nrecords,nceldas)
    integer, intent(out) :: Res
    !f2py intent(in) :: nrecords,nceldas,ruta,records
    !f2py intent(out) :: vect
    !Variables locales
    integer i 
    !Lectura 
    open(10,file=ruta,form='unformatted',status='old',access='direct',RECL=4*nceldas)
	do i=1,nrecords
	    read(10,rec=records(i),iostat=Res) vect(i,:)
	    if (Res.ne.0) print *, 'Error: Se ha tratado de leer un valor fuera del rango'
	enddo
    close(10)
end subroutine
