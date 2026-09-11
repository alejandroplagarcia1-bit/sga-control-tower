import random, sys, os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import pandas as pd
from PIL import Image
from io import BytesIO

# MongoDB
try:
    import pymongo
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client["gestion_almacen"]
    mongo_disponible = True
except Exception:
    mongo_disponible = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Nombres y datos
NOMBRES = ["Alejandro", "Carlos", "David", "Javier", "Manuel", "María", "Carmen", "Ana", "Laura"]
APELLIDOS = ["García", "González", "Rodríguez", "Fernández", "López", "Martínez", "Sánchez", "Pérez"]
LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

def generar_nombre() -> str:
    return f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"

def generar_dni() -> str:
    num = random.randint(10000000, 99999999)
    return f"{num}{LETRAS_DNI[num % 23]}"


# =====================================================================
# MODELOS DE DATOS
# =====================================================================

@dataclass
class Operario:
    id_operario: str
    nombre: str
    dni: str
    ett: str
    turno: str
    hora_ingreso: str = "--:--:--"
    hora_salida: str = "--:--:--"
    estado: str = "PENDIENTE"
    observacion: str = ""  # Para notas de faltas u otros eventos
    salario: float = 0.0  # Salario mensual
    dias_falta: int = 0  # Contador de días de falta

@dataclass
class Palet:
    id_palet: str
    sku_producto: str
    nombre_producto: str
    pasillo: str
    nivel: str
    posicion: int  # 1-20 posiciones por nivel
    operario_asignado: str = ""
    estado: str = "ubicado"  # ubicado, en_transito, pendiente
    fecha_ubicacion: str = ""

@dataclass
class Producto:
    sku: str
    nombre: str
    pasillo: str
    nivel: str
    stock: int
    rotacion: str
    palet_id: str = ""

@dataclass
class Stock:
    producto_sku: str
    ubicacion: str
    cantidad_palets: int

@dataclass
class Albarani:
    id_albarani: str
    tipo: str  # "entrega", "recogida", "entrada"
    fecha: str
    producto: str
    cantidad: int
    fotos: List[str] = field(default_factory=list)
    estado: str = "pendiente"

@dataclass
class Camion:
    id_camion: str
    matricula: str
    chofer: str
    dni_chofer: str
    capacidad_palets: int
    estado: str = "disponible"
    palets_asignados: List[str] = field(default_factory=list)  # IDs de palets que lleva

class SistemaAlmacen:
    PRODUCTOS_ALMACEN = [
        # HARINAS
        ("HAR-TRIG", "Harina de Trigo Premium 25kg", "Alta"),
        ("HAR-INTE", "Harina Integral 25kg", "Alta"),
        ("HAR-PAST", "Harina Pastelera Especial 25kg", "Alta"),
        ("HAR-CORN", "Harina de Maíz 25kg", "Media"),
        
        # AZÚCARES
        ("AZU-NORM", "Azúcar Blanco Refinado 50kg", "Alta"),
        ("AZU-MORE", "Azúcar Moreno 50kg", "Alta"),
        ("AZU-GLAS", "Azúcar Glas/Impalpable 50kg", "Alta"),
        ("AZU-MOSC", "Azúcar Moscovado 25kg", "Media"),
        
        # GRASAS Y ACEITES
        ("MAN-PURA", "Mantequilla Pura 10kg", "Alta"),
        ("MAN-VEGE", "Mantequilla Vegana 10kg", "Media"),
        ("ACE-OLIV", "Aceite Oliva Extra Virgen 20L", "Media"),
        ("ACE-GIRA", "Aceite de Girasol 20L", "Alta"),
        ("MARG-PRO", "Margarina Profesional 10kg", "Media"),
        
        # AGENTES DE LEVADURA
        ("LEV-FRES", "Levadura Fresca 500g paquetes", "Media"),
        ("LEV-SECP", "Levadura Seca 250g", "Media"),
        ("POL-HORN", "Polvo para Hornear 1kg", "Alta"),
        ("BICA-SOD", "Bicarbonato de Sodio 1kg", "Media"),
        
        # CHOCOLATE
        ("CHO-BLAC", "Chocolate Negro Cobertura 70% 10kg", "Alta"),
        ("CHO-LECH", "Chocolate con Leche 38% 10kg", "Alta"),
        ("CHO-BLAN", "Chocolate Blanco Cobertura 10kg", "Alta"),
        ("CHO-POLV", "Cacao en Polvo 1kg", "Alta"),
        ("CHO-VIRU", "Virutas de Chocolate Surtidas 5kg", "Media"),
        
        # FRUTAS SECAS
        ("FRU-PASA", "Pasas Sultanas 5kg", "Media"),
        ("FRU-ARAN", "Arándanos Deshidratados 2kg", "Media"),
        ("FRU-NUER", "Nueces Trozadas 5kg", "Media"),
        ("FRU-ALME", "Almendras Laminadas 5kg", "Media"),
        ("FRU-CIST", "Ciruelas Pasa Premium 3kg", "Media"),
        ("FRU-COCE", "Coco Rallado 5kg", "Media"),
        
        # ESENCIAS Y SABORIZANTES
        ("ESEN-VAN", "Esencia de Vainilla 1L", "Media"),
        ("ESEN-ALM", "Esencia de Almendra 1L", "Media"),
        ("ESEN-RON", "Esencia de Ron 500ml", "Media"),
        ("ESEN-NAR", "Esencia de Naranja 500ml", "Media"),
        ("ESEN-LIM", "Esencia de Limón 500ml", "Media"),
        
        # LECHE Y PRODUCTOS LÁCTEOS
        ("LECH-POL", "Leche en Polvo 1kg", "Media"),
        ("CREMA-PA", "Crema Pastelera Preparada 1kg", "Alta"),
        ("QUESO-MA", "Queso Mascarpone 500g", "Alta"),
        ("YOGUR-GR", "Yogur Griego 1L", "Media"),
        
        # COBERTURAS Y DECORACIONES
        ("COB-FRES", "Cobertura Fondant Surtida 5kg", "Media"),
        ("DEC-PERL", "Perlas de Azúcar Surtidas 1kg", "Media"),
        ("DEC-MENT", "Mentas de Chocolate 1kg", "Media"),
        ("DEC-CAJA", "Cajitas Decorativas Surtidas 100ud", "Baja"),
        ("GLACE-RE", "Glaseado Real Preparado 1kg", "Media"),
        
        # ESPECIAS Y CONDIMENTOS
        ("ESPE-CAN", "Canela Molida Premium 250g", "Media"),
        ("ESPE-NUE", "Nuez Moscada Molida 250g", "Media"),
        ("ESPE-AJ", "Ajonjolí/Sésamo 1kg", "Baja"),
        ("ESPE-PIN", "Pimienta Negra Molida 250g", "Baja"),
        ("ESPE-CLO", "Clavo de Olor 100g", "Baja"),
        
        # BEBIDAS Y COMPLEMENTOS
        ("BEB-CAFE", "Café Molido Premium 1kg", "Media"),
        ("BEB-TELE", "Té Gourmet Surtido 500g", "Baja"),
        ("BEB-AGUA", "Agua Destilada 20L", "Media"),
        ("BEBREF-L", "Refresco Limón 6 botellas", "Media"),
        
        # MOLDES Y BANDEJAS (productos anexos)
        ("MOL-CAKE", "Moldes para Cake Surtidos 12ud", "Baja"),
        ("MOL-DONAS", "Moldes para Donuts 12ud", "Baja"),
        ("BAND-HOJ", "Bandejas de Hoja Aluminio 100ud", "Baja"),
        ("PAPE-HOR", "Papel de Hornear 100m", "Media"),
        
        # COLORANTES Y GELIFICANTES
        ("COLOR-AL", "Colorante Alimentario Surtido 30ml", "Baja"),
        ("GELA-POL", "Gelatina en Polvo 1kg", "Media"),
        ("ALMI-MAI", "Almidón de Maíz 1kg", "Media"),
    ]

    def __init__(self):
        self.operarios: List[Operario] = []
        self.inventario: List[Producto] = []
        self.palets: List[Palet] = []  # NUEVO: Lista de palets
        self.stock_reserva: Dict[str, int] = {}
        self.albaranes: List[Albarani] = []
        self.camiones: List[Camion] = []
        self.conteo_etts: Dict[str, Dict[str, int]] = {}
        self._inicializar_inventario()
        self._inicializar_camiones()
        self._inicializar_palets()  # NUEVO: Crear palets

    def _inicializar_inventario(self):
        pasillos_activos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        niveles = ['Suelo', 'Nivel 1', 'Nivel 2', 'Nivel 3']
        idx = 1
        for sku, nombre, rotacion in self.PRODUCTOS_ALMACEN:
            self.inventario.append(Producto(
                sku=sku, nombre=nombre, pasillo=random.choice(pasillos_activos),
                nivel=random.choice(niveles), stock=random.randint(5, 20),
                rotacion=rotacion, palet_id=f"PAL-{idx:04d}"
            ))
            idx += 1
            self.stock_reserva[sku] = random.randint(3, 10)

    def _inicializar_camiones(self):
        for i in range(1, 5):
            self.camiones.append(Camion(
                id_camion=f"CAM-{i:03d}",
                matricula=f"{random.randint(1000, 9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                chofer=generar_nombre(),
                dni_chofer=generar_dni(),
                capacidad_palets=random.randint(20, 30)
            ))

    def _inicializar_palets(self):
        """Crea 90+ palets iniciales para cada producto y los distribuye en las estanterías"""
        pasillos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        niveles = ['Suelo', 'Nivel 1', 'Nivel 2', 'Nivel 3']
        id_palet = 1
        
        # Crear más palets por producto para alcanzar ~90 palets
        for producto in self.inventario:
            # Productos de alta rotación: 2-3 palets
            # Productos de media rotación: 1-2 palets
            # Productos de baja rotación: 1 palet
            if producto.rotacion == "Alta":
                cantidad_palets = random.randint(2, 3)
            elif producto.rotacion == "Media":
                cantidad_palets = random.randint(1, 2)
            else:
                cantidad_palets = 1
            
            for _ in range(cantidad_palets):
                palet = Palet(
                    id_palet=f"PAL-{id_palet:05d}",
                    sku_producto=producto.sku,
                    nombre_producto=producto.nombre,
                    pasillo=random.choice(pasillos),
                    nivel=random.choice(niveles),
                    posicion=random.randint(1, 20),
                    operario_asignado="",
                    estado="ubicado",
                    fecha_ubicacion=datetime.now().strftime("%d/%m/%Y %H:%M")
                )
                self.palets.append(palet)
                id_palet += 1

    def obtener_palets_por_ubicacion(self, pasillo: str, nivel: str = None) -> List[Palet]:
        """Retorna todos los palets en una ubicación específica"""
        if nivel:
            return [p for p in self.palets if p.pasillo == pasillo and p.nivel == nivel]
        return [p for p in self.palets if p.pasillo == pasillo]
    
    def asignar_palets_random_a_camion(self, id_camion: str, cantidad: int = None):
        """Asigna palets random a un camión específico"""
        camion = next((c for c in self.camiones if c.id_camion == id_camion), None)
        if not camion:
            return False
        
        # Limpiar palets previos
        palets_libres = [p for p in self.palets if p.id_palet not in [c for cam in self.camiones for c in cam.palets_asignados]]
        
        if not palets_libres:
            return False
        
        # Asignar cantidad random (hasta capacidad)
        if cantidad is None:
            cantidad = min(random.randint(3, 8), len(palets_libres), camion.capacidad_palets)
        
        palets_asignados = random.sample(palets_libres, min(cantidad, len(palets_libres)))
        camion.palets_asignados = [p.id_palet for p in palets_asignados]
        return True
    
    def obtener_palets_de_camion(self, id_camion: str) -> List[Palet]:
        """Retorna todos los palets asignados a un camión"""
        camion = next((c for c in self.camiones if c.id_camion == id_camion), None)
        if not camion:
            return []
        return [p for p in self.palets if p.id_palet in camion.palets_asignados]
    
    def remover_palet_de_camion(self, id_camion: str, id_palet: str):
        """Remueve un palet de un camión"""
        camion = next((c for c in self.camiones if c.id_camion == id_camion), None)
        if camion and id_palet in camion.palets_asignados:
            camion.palets_asignados.remove(id_palet)
            return True
        return False
    
    def reasignar_palet_ubicacion(self, id_palet: str, pasillo: str, nivel: str, posicion: int):
        """Reasigna un palet a una nueva ubicación en el almacén"""
        palet = next((p for p in self.palets if p.id_palet == id_palet), None)
        if palet:
            palet.pasillo = pasillo
            palet.nivel = nivel
            palet.posicion = posicion
            palet.fecha_ubicacion = datetime.now().strftime("%d/%m/%Y %H:%M")
            return True
        return False

    def obtener_palets_por_producto(self, sku: str) -> List[Palet]:
        """Retorna todos los palets de un producto"""
        return [p for p in self.palets if p.sku_producto == sku]

    def mover_palet(self, id_palet: str, nuevo_pasillo: str, nuevo_nivel: str, posicion: int, operario: str = "") -> bool:
        """Mueve un palet a una nueva ubicación"""
        for palet in self.palets:
            if palet.id_palet == id_palet:
                palet.pasillo = nuevo_pasillo
                palet.nivel = nuevo_nivel
                palet.posicion = posicion
                palet.operario_asignado = operario
                palet.fecha_ubicacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                return True
        return False

    def asignar_palet_a_operario(self, id_palet: str, id_operario: str) -> bool:
        """Asigna un palet a un operario para que lo ubique"""
        for palet in self.palets:
            if palet.id_palet == id_palet:
                palet.operario_asignado = id_operario
                palet.estado = "en_transito"
                return True
        return False

    def obtener_palets_sin_ubicar(self) -> List[Palet]:
        """Retorna palets pendientes de ubicación"""
        return [p for p in self.palets if p.estado == "pendiente"]

    def obtener_palets_por_operario(self, id_operario: str) -> List[Palet]:
        """Retorna palets asignados a un operario"""
        return [p for p in self.palets if p.operario_asignado == id_operario]

    CUPOS_TURNO = {"Mañana": 30, "Tarde": 20, "Noche": 10}

    def registrar_ett(self, nombre_ett: str) -> str:
        ett = nombre_ett.strip().upper()
        if ett not in self.conteo_etts:
            self.conteo_etts[ett] = {"Mañana": 0, "Tarde": 0, "Noche": 0}
        return ett

    def agregar_operario(self, op: Operario) -> tuple:
        ett = self.registrar_ett(op.ett)
        op.ett = ett
        turno = op.turno.capitalize()
        
        if turno not in self.CUPOS_TURNO:
            return False, f"Turno {turno} no válido."
        
        cupo_actual = self.conteo_etts[ett][turno]
        cupo_max = self.CUPOS_TURNO[turno]
        
        if cupo_actual >= cupo_max:
            return False, f"⛔ CUPO LLENO: {ett} en {turno} ({cupo_actual}/{cupo_max})."
        
        self.conteo_etts[ett][turno] += 1
        self.operarios.append(op)
        return True, "Operario registrado"

    def poblar_ett(self, nombre_ett: str):
        ett = nombre_ett.strip().upper()
        plan = [("Mañana", 30), ("Tarde", 20), ("Noche", 10)]
        for turno, cant in plan:
            for i in range(1, cant + 1):
                op = Operario(
                    id_operario=f"{ett[:3]}-{turno[0]}-{i:03d}",
                    nombre=generar_nombre(),
                    dni=generar_dni(),
                    ett=ett,
                    turno=turno
                )
                self.agregar_operario(op)

    def obtener_faltantes(self, turno: str) -> List[Operario]:
        return [op for op in self.operarios if op.turno == turno and op.estado == "PENDIENTE"]

    def obtener_presentes(self, turno: str) -> List[Operario]:
        return [op for op in self.operarios if op.turno == turno and op.estado == "PRESENTE"]

    def activar_modo_verano(self):
        for prod in self.inventario:
            if prod.rotacion == "Alta":
                prod.pasillo = "A"
                prod.nivel = "Suelo"

    def activar_modo_invierno(self):
        for prod in self.inventario:
            if prod.rotacion == "Alta":
                prod.pasillo = random.choice(['A', 'B', 'C'])
                prod.nivel = random.choice(['Suelo', 'Nivel 1'])

    def obtener_alerta_reposicion(self) -> List[str]:
        alertas = []
        for prod in self.inventario:
            if prod.stock < 3 and prod.rotacion == "Alta":
                reserva = self.stock_reserva.get(prod.sku, 0)
                if reserva > 0:
                    alertas.append(f"🔴 Reabastecer {prod.nombre} desde Pasillo I/J ({reserva} palets)")
        return alertas

    def mover_palet(self, sku: str, nuevo_pasillo: str, nuevo_nivel: str) -> bool:
        for prod in self.inventario:
            if prod.sku == sku:
                prod.pasillo = nuevo_pasillo
                prod.nivel = nuevo_nivel
                return True
        return False

    def crear_albarani(self, tipo: str, producto: str, cantidad: int, fotos: List[str] = None):
        id_alb = f"ALB-{len(self.albaranes)+1:05d}"
        alb = Albarani(
            id_albarani=id_alb,
            tipo=tipo,
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
            producto=producto,
            cantidad=cantidad,
            fotos=fotos or [],
            estado="pendiente"
        )
        self.albaranes.append(alb)
        return id_alb

    def descargar_personal_excel(self, ruta="personal_control.xlsx"):
        """Descarga información del personal con horarios, salarios y bajas"""
        data = []
        for op in self.operarios:
            estado_baja = "SÍ" if op.estado == "AUSENTE" else "NO"
            data.append({
                "ID": op.id_operario,
                "Nombre": op.nombre,
                "DNI": op.dni,
                "ETT": op.ett,
                "Turno": op.turno,
                "Salario (€)": f"{op.salario:.2f}",
                "Entrada": op.hora_ingreso if op.hora_ingreso != "--:--:--" else "-",
                "Salida": op.hora_salida if op.hora_salida != "--:--:--" else "-",
                "Estado": op.estado,
                "En Baja": estado_baja,
                "Días Falta": op.dias_falta,
                "Motivo": op.observacion if op.observacion else "-"
            })
        df = pd.DataFrame(data)
        df.to_excel(ruta, index=False)
        messagebox.showinfo("✅ Descarga Exitosa", f"Personal descargado en:\n{ruta}")
        return ruta


# =====================================================================
# DASHBOARD PRINCIPAL (CUSTOMTKINTER)
# =====================================================================

class DashboardApp(ctk.CTk):
    def __init__(self, sistema: SistemaAlmacen):
        super().__init__()
        self.sistema = sistema
        self.title("SAP ALMACÉN - Control Total")
        self.geometry("1600x900")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.ett_filtrada = None  # Inicializar filtro de ETT

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Pestañas principales
        self.tab_acceso = self.tabview.add("🚪 Acceso & Turnos")
        self.tab_almacen = self.tabview.add("📦 Almacén")
        self.tab_palets = self.tabview.add("📍 Palets & Ubicaciones")
        self.tab_albaranes = self.tabview.add("📋 Albaranes")
        self.tab_camiones = self.tabview.add("🚚 Flota Camiones")

        self.setup_tab_acceso()
        self.setup_tab_almacen()
        self.setup_tab_palets()
        self.setup_tab_albaranes()
        self.setup_tab_camiones()
        
        # Cargar personas automáticamente
        self._cargar_personas_iniciales()

    # ========================== PESTAÑA: ACCESO ==========================
    def setup_tab_acceso(self):
        self.tab_acceso.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_acceso.grid_rowconfigure(1, weight=1)

        # Panel de control superior
        top_panel = ctk.CTkFrame(self.tab_acceso)
        top_panel.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        top_panel.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(top_panel, text="Nombre", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=2)
        self.entry_nombre = ctk.CTkEntry(top_panel, width=120, height=28)
        self.entry_nombre.grid(row=1, column=0, padx=2)

        ctk.CTkLabel(top_panel, text="DNI", font=ctk.CTkFont(size=10)).grid(row=0, column=1, padx=2)
        self.entry_dni = ctk.CTkEntry(top_panel, width=100, height=28)
        self.entry_dni.grid(row=1, column=1, padx=2)

        ctk.CTkLabel(top_panel, text="ETT", font=ctk.CTkFont(size=10)).grid(row=0, column=2, padx=2)
        self.combo_ett = ctk.CTkOptionMenu(top_panel, values=["RANDSTAD", "ADECCO", "MANPOWER"], width=100, height=28)
        self.combo_ett.grid(row=1, column=2, padx=2)

        ctk.CTkLabel(top_panel, text="Turno", font=ctk.CTkFont(size=10)).grid(row=0, column=3, padx=2)
        self.combo_turno = ctk.CTkOptionMenu(top_panel, values=["Mañana", "Tarde", "Noche"], width=100, height=28)
        self.combo_turno.grid(row=1, column=3, padx=2)

        self.btn_registrar = ctk.CTkButton(top_panel, text="➕", width=50, height=28, command=self.registrar_persona)
        self.btn_registrar.grid(row=1, column=4, padx=2)

        self.btn_cargar_randstad = ctk.CTkButton(top_panel, text="🏢 RANDSTAD", height=28, fg_color="#0284c7", command=lambda: self.filtrar_por_ett("RANDSTAD"))
        self.btn_cargar_randstad.grid(row=0, column=5, padx=2)
        self.btn_cargar_adecco = ctk.CTkButton(top_panel, text="🏢 ADECCO", height=28, fg_color="#d97706", command=lambda: self.filtrar_por_ett("ADECCO"))
        self.btn_cargar_adecco.grid(row=1, column=5, padx=2)
        self.btn_cargar_manpower = ctk.CTkButton(top_panel, text="🏢 MANPOWER", height=28, fg_color="#7c3aed", command=lambda: self.filtrar_por_ett("MANPOWER"))
        self.btn_cargar_manpower.grid(row=0, column=6, padx=2)
        
        self.btn_ver_todos = ctk.CTkButton(top_panel, text="👥 Ver Todos", height=28, fg_color="#16a34a", command=lambda: self.filtrar_por_ett(None))
        self.btn_ver_todos.grid(row=1, column=6, padx=2)

        # Tablas mejoradas: Pendientes, Dentro, Faltantes
        frame_pendientes = ctk.CTkFrame(self.tab_acceso)
        frame_pendientes.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frame_pendientes.grid_rowconfigure(1, weight=1)
        frame_pendientes.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_pendientes, text="⏳ PENDIENTES DE ENTRAR (2x clic: Fichar Entrada)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
        self.tree_pend = ttk.Treeview(frame_pendientes, columns=("ID", "Nombre", "ETT", "Turno", "Obs"), height=25)
        self.tree_pend.column("#0", width=0)
        self.tree_pend.column("ID", width=70, anchor="center")
        self.tree_pend.column("Nombre", width=110, anchor="w")
        self.tree_pend.column("ETT", width=80, anchor="center")
        self.tree_pend.column("Turno", width=60, anchor="center")
        self.tree_pend.column("Obs", width=80, anchor="w")
        self.tree_pend.heading("ID", text="ID")
        self.tree_pend.heading("Nombre", text="Nombre")
        self.tree_pend.heading("ETT", text="ETT")
        self.tree_pend.heading("Turno", text="Turno")
        self.tree_pend.heading("Obs", text="Observación")
        self.tree_pend.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_pend.bind("<Double-1>", lambda e: self.fichar_entrada())

        frame_dentro = ctk.CTkFrame(self.tab_acceso)
        frame_dentro.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        frame_dentro.grid_rowconfigure(1, weight=1)
        frame_dentro.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_dentro, text="🟢 DENTRO DEL ALMACÉN (2x clic: Fichar Salida)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
        self.tree_dentro = ttk.Treeview(frame_dentro, columns=("ID", "Entrada", "Nombre", "ETT", "Turno", "Obs"), height=25)
        self.tree_dentro.column("#0", width=0)
        self.tree_dentro.column("ID", width=70, anchor="center")
        self.tree_dentro.column("Entrada", width=75, anchor="center")
        self.tree_dentro.column("Nombre", width=95, anchor="w")
        self.tree_dentro.column("ETT", width=70, anchor="center")
        self.tree_dentro.column("Turno", width=55, anchor="center")
        self.tree_dentro.column("Obs", width=70, anchor="w")
        self.tree_dentro.heading("ID", text="ID")
        self.tree_dentro.heading("Entrada", text="Entrada")
        self.tree_dentro.heading("Nombre", text="Nombre")
        self.tree_dentro.heading("ETT", text="ETT")
        self.tree_dentro.heading("Turno", text="Turno")
        self.tree_dentro.heading("Obs", text="Observación")
        self.tree_dentro.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_dentro.bind("<Double-1>", lambda e: self.fichar_salida())

        frame_faltan = ctk.CTkFrame(self.tab_acceso)
        frame_faltan.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        frame_faltan.grid_rowconfigure(2, weight=1)
        frame_faltan.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_faltan, text="❌ FALTANTES HOY", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
        
        # Sub-panel para turno y observación
        subpanel_faltan = ctk.CTkFrame(frame_faltan)
        subpanel_faltan.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        subpanel_faltan.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(subpanel_faltan, text="Turno:", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=2)
        self.combo_turno_faltan = ctk.CTkOptionMenu(subpanel_faltan, values=["Todos", "Mañana", "Tarde", "Noche"], width=100, height=28, command=self.mostrar_faltantes)
        self.combo_turno_faltan.grid(row=0, column=1, columnspan=2, padx=2, sticky="ew")

        ctk.CTkLabel(subpanel_faltan, text="Motivo:", font=ctk.CTkFont(size=10)).grid(row=1, column=0, padx=2)
        self.entry_obs_falta = ctk.CTkEntry(subpanel_faltan, width=150, height=28, placeholder_text="Enfermedad, vacaciones...")
        self.entry_obs_falta.grid(row=1, column=1, columnspan=2, padx=2, sticky="ew")

        self.tree_faltan = ttk.Treeview(frame_faltan, columns=("Nombre", "Turno", "Motivo", "Act"), height=21)
        self.tree_faltan.column("#0", width=0)
        self.tree_faltan.column("Nombre", width=100, anchor="w")
        self.tree_faltan.column("Turno", width=60, anchor="center")
        self.tree_faltan.column("Motivo", width=90, anchor="w")
        self.tree_faltan.column("Act", width=50, anchor="center")
        self.tree_faltan.heading("Nombre", text="Nombre")
        self.tree_faltan.heading("Turno", text="Turno")
        self.tree_faltan.heading("Motivo", text="Motivo")
        self.tree_faltan.heading("Act", text="Acción")
        self.tree_faltan.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_faltan.bind("<Double-1>", lambda e: self.marcar_falta_seleccionado())

        self.actualizar_acceso()

    # ========================== PESTAÑA: ALMACÉN ==========================
    def setup_tab_almacen(self):
        self.tab_almacen.grid_columnconfigure((0, 1), weight=1)
        self.tab_almacen.grid_rowconfigure(1, weight=1)

        # Panel de control
        top_panel = ctk.CTkFrame(self.tab_almacen)
        top_panel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_verano = ctk.CTkButton(top_panel, text="☀️ Modo VERANO", fg_color="#ea580c", height=32, command=self.activar_verano)
        self.btn_verano.grid(row=0, column=0, padx=5)

        self.btn_invierno = ctk.CTkButton(top_panel, text="❄️ Modo INVIERNO", fg_color="#0284c7", height=32, command=self.activar_invierno)
        self.btn_invierno.grid(row=0, column=1, padx=5)

        self.btn_alertas = ctk.CTkButton(top_panel, text="🔴 Ver Alertas", fg_color="#dc2626", height=32, command=self.mostrar_alertas)
        self.btn_alertas.grid(row=0, column=2, padx=5)

        self.btn_exportar = ctk.CTkButton(top_panel, text="� Descargar Personal", fg_color="#7c3aed", height=32, command=lambda: self.sistema.descargar_personal_excel())
        self.btn_exportar.grid(row=0, column=3, padx=5)

        # Tabla inventario
        frame_inv = ctk.CTkFrame(self.tab_almacen)
        frame_inv.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        frame_inv.grid_rowconfigure(2, weight=1)
        frame_inv.grid_columnconfigure(0, weight=1)

        # Buscador
        titulo_frame = ctk.CTkFrame(frame_inv)
        titulo_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        titulo_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(titulo_frame, text="📍 INVENTARIO ACTIVO", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)

        search_frame = ctk.CTkFrame(titulo_frame)
        search_frame.grid(row=0, column=1, sticky="e", padx=5)

        ctk.CTkLabel(search_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.entry_buscar_inv = ctk.CTkEntry(search_frame, width=200, height=28, placeholder_text="SKU o Nombre del producto...")
        self.entry_buscar_inv.pack(side="left", padx=5)
        self.entry_buscar_inv.bind("<KeyRelease>", self.filtrar_inventario)

        # Tabla
        self.tree_inv = ttk.Treeview(frame_inv, columns=("SKU", "Producto", "Pasillo", "Nivel", "Stock", "Reserva", "Rotación"))
        self.tree_inv.column("#0", width=0)
        self.tree_inv.column("SKU", width=90, anchor="center")
        self.tree_inv.column("Producto", width=120, anchor="w")
        self.tree_inv.column("Pasillo", width=70, anchor="center")
        self.tree_inv.column("Nivel", width=90, anchor="center")
        self.tree_inv.column("Stock", width=60, anchor="center")
        self.tree_inv.column("Reserva", width=60, anchor="center")
        self.tree_inv.column("Rotación", width=70, anchor="center")
        self.tree_inv.heading("SKU", text="SKU")
        self.tree_inv.heading("Producto", text="Producto")
        self.tree_inv.heading("Pasillo", text="Pasillo")
        self.tree_inv.heading("Nivel", text="Nivel")
        self.tree_inv.heading("Stock", text="Stock")
        self.tree_inv.heading("Reserva", text="Reserva I/J")
        self.tree_inv.heading("Rotación", text="Rotación")
        self.tree_inv.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.actualizar_almacen()

    # ========================== PESTAÑA: PALETS & UBICACIONES ==========================
    def setup_tab_palets(self):
        self.tab_palets.grid_columnconfigure((0, 1), weight=1)
        self.tab_palets.grid_rowconfigure(2, weight=1)

        # Panel 1: Buscar y filtrar palets
        panel_busqueda = ctk.CTkFrame(self.tab_palets)
        panel_busqueda.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        panel_busqueda.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(panel_busqueda, text="🔍 Buscar Palet", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=2)
        self.entry_buscar_palet = ctk.CTkEntry(panel_busqueda, width=120, height=28, placeholder_text="PAL-00001")
        self.entry_buscar_palet.grid(row=1, column=0, padx=2)
        self.entry_buscar_palet.bind("<KeyRelease>", lambda e: self.filtrar_palets())

        ctk.CTkLabel(panel_busqueda, text="Pasillo", font=ctk.CTkFont(size=10)).grid(row=0, column=1, padx=2)
        self.combo_pasillo = ctk.CTkOptionMenu(panel_busqueda, values=["Todos", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"], width=100, height=28, command=self.filtrar_palets)
        self.combo_pasillo.grid(row=1, column=1, padx=2)

        ctk.CTkLabel(panel_busqueda, text="Nivel", font=ctk.CTkFont(size=10)).grid(row=0, column=2, padx=2)
        self.combo_nivel = ctk.CTkOptionMenu(panel_busqueda, values=["Todos", "Suelo", "Nivel 1", "Nivel 2", "Nivel 3"], width=100, height=28, command=self.filtrar_palets)
        self.combo_nivel.grid(row=1, column=2, padx=2)

        self.btn_refresh_palets = ctk.CTkButton(panel_busqueda, text="🔄 Actualizar", width=100, height=28, command=self.actualizar_palets)
        self.btn_refresh_palets.grid(row=1, column=3, padx=2)

        self.lbl_total_palets = ctk.CTkLabel(panel_busqueda, text="", font=ctk.CTkFont(size=10))
        self.lbl_total_palets.grid(row=1, column=4, columnspan=2, padx=5)

        # Panel 2: Mover palet
        panel_mover = ctk.CTkFrame(self.tab_palets)
        panel_mover.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        panel_mover.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(panel_mover, text="📍 MOVER PALET", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, columnspan=6, sticky="w", padx=5, pady=3)

        ctk.CTkLabel(panel_mover, text="ID Palet", font=ctk.CTkFont(size=9)).grid(row=1, column=0, padx=2)
        self.entry_mover_id = ctk.CTkEntry(panel_mover, width=100, height=28)
        self.entry_mover_id.grid(row=1, column=0, padx=2)

        ctk.CTkLabel(panel_mover, text="Pasillo", font=ctk.CTkFont(size=9)).grid(row=1, column=1, padx=2)
        self.combo_pasillo_dest = ctk.CTkOptionMenu(panel_mover, values=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"], width=80, height=28)
        self.combo_pasillo_dest.grid(row=1, column=1, padx=2)

        ctk.CTkLabel(panel_mover, text="Nivel", font=ctk.CTkFont(size=9)).grid(row=1, column=2, padx=2)
        self.combo_nivel_dest = ctk.CTkOptionMenu(panel_mover, values=["Suelo", "Nivel 1", "Nivel 2", "Nivel 3"], width=100, height=28)
        self.combo_nivel_dest.grid(row=1, column=2, padx=2)

        ctk.CTkLabel(panel_mover, text="Posición", font=ctk.CTkFont(size=9)).grid(row=1, column=3, padx=2)
        self.entry_posicion = ctk.CTkEntry(panel_mover, width=60, height=28, placeholder_text="1-20")
        self.entry_posicion.grid(row=1, column=3, padx=2)

        ctk.CTkLabel(panel_mover, text="Operario", font=ctk.CTkFont(size=9)).grid(row=1, column=4, padx=2)
        self.combo_operario = ctk.CTkOptionMenu(panel_mover, values=["Sin asignar"] + [op.id_operario for op in self.sistema.operarios if op.estado == "PRESENTE"], width=100, height=28)
        self.combo_operario.grid(row=1, column=4, padx=2)

        self.btn_mover = ctk.CTkButton(panel_mover, text="✅ MOVER", fg_color="#16a34a", height=28, command=self.mover_palet_accion)
        self.btn_mover.grid(row=1, column=5, padx=5)

        # Tabla de palets
        frame_tabla = ctk.CTkFrame(self.tab_palets)
        frame_tabla.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        frame_tabla.grid_rowconfigure(1, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_tabla, text="📦 PALETS EN ALMACÉN", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)

        self.tree_palets = ttk.Treeview(frame_tabla, columns=("ID", "Producto", "Pasillo", "Nivel", "Pos", "Operario", "Estado", "Fecha"))
        self.tree_palets.column("#0", width=0)
        for col, width in [("ID", 90), ("Producto", 120), ("Pasillo", 70), ("Nivel", 100), ("Pos", 40), ("Operario", 90), ("Estado", 80), ("Fecha", 130)]:
            self.tree_palets.column(col, width=width, anchor="center")
            self.tree_palets.heading(col, text=col)
        self.tree_palets.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.actualizar_palets()

    # ========================== PESTAÑA: ALBARANES ==========================
    def setup_tab_albaranes(self):
        self.tab_albaranes.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_albaranes.grid_rowconfigure(1, weight=1)

        # Panel superior
        top = ctk.CTkFrame(self.tab_albaranes)
        top.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(top, text="Tipo", font=ctk.CTkFont(size=10)).grid(row=0, column=0)
        self.combo_tipo_alb = ctk.CTkOptionMenu(top, values=["entrega", "recogida", "entrada"], width=100, height=28)
        self.combo_tipo_alb.grid(row=1, column=0, padx=2)

        ctk.CTkLabel(top, text="Producto", font=ctk.CTkFont(size=10)).grid(row=0, column=1)
        self.combo_prod = ctk.CTkOptionMenu(top, values=[p[1] for p in SistemaAlmacen.PRODUCTOS_ALMACEN], width=120, height=28)
        self.combo_prod.grid(row=1, column=1, padx=2)

        ctk.CTkLabel(top, text="Cantidad", font=ctk.CTkFont(size=10)).grid(row=0, column=2)
        self.entry_cant = ctk.CTkEntry(top, width=80, height=28)
        self.entry_cant.grid(row=1, column=2, padx=2)

        self.btn_foto = ctk.CTkButton(top, text="📸 Añadir Foto", width=100, height=28, command=self.cargar_foto)
        self.btn_foto.grid(row=1, column=3, padx=2)

        self.btn_crear_alb = ctk.CTkButton(top, text="✅ Crear Albarani", width=100, height=28, command=self.crear_albarani)
        self.btn_crear_alb.grid(row=1, column=4, padx=2)

        self.fotos_cargadas = []
        self.lbl_fotos = ctk.CTkLabel(top, text="Sin fotos", font=ctk.CTkFont(size=9))
        self.lbl_fotos.grid(row=1, column=5, padx=2)

        # Tabla albaranes
        frame_alb = ctk.CTkFrame(self.tab_albaranes)
        frame_alb.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        frame_alb.grid_rowconfigure(1, weight=1)
        frame_alb.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_alb, text="📋 ALBARANES", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
        self.tree_alb = ttk.Treeview(frame_alb, columns=("ID", "Tipo", "Fecha", "Producto", "Cant", "Fotos", "Estado"))
        self.tree_alb.column("#0", width=0)
        for col, width in [("ID", 80), ("Tipo", 80), ("Fecha", 120), ("Producto", 120), ("Cant", 50), ("Fotos", 50), ("Estado", 80)]:
            self.tree_alb.column(col, width=width, anchor="center")
            self.tree_alb.heading(col, text=col)
        self.tree_alb.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    # ========================== PESTAÑA: CAMIONES ==========================
    def setup_tab_camiones(self):
        self.tab_camiones.grid_columnconfigure((0, 1), weight=1)
        self.tab_camiones.grid_rowconfigure(2, weight=1)

        # Panel superior
        top = ctk.CTkFrame(self.tab_camiones)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top.pack_propagate(False)

        self.btn_generar_random = ctk.CTkButton(top, text="🎲 Generar Asignación Random", width=150, height=28, command=self.generar_palets_random)
        self.btn_generar_random.pack(side="left", padx=5)

        self.btn_refresh_cam = ctk.CTkButton(top, text="🔄 Actualizar", width=100, height=28, command=self.actualizar_camiones)
        self.btn_refresh_cam.pack(side="left", padx=5)

        # Panel de reasignación
        panel_reasign = ctk.CTkFrame(self.tab_camiones)
        panel_reasign.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        panel_reasign.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(panel_reasign, text="ID Palet a Mover", font=ctk.CTkFont(size=10)).grid(row=0, column=0)
        self.entry_palet_mover = ctk.CTkEntry(panel_reasign, width=100, height=28)
        self.entry_palet_mover.grid(row=1, column=0, padx=2)

        ctk.CTkLabel(panel_reasign, text="Pasillo", font=ctk.CTkFont(size=10)).grid(row=0, column=1)
        self.combo_pasillo_mover = ctk.CTkOptionMenu(panel_reasign, values=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'], width=80, height=28)
        self.combo_pasillo_mover.grid(row=1, column=1, padx=2)

        ctk.CTkLabel(panel_reasign, text="Nivel", font=ctk.CTkFont(size=10)).grid(row=0, column=2)
        self.combo_nivel_mover = ctk.CTkOptionMenu(panel_reasign, values=["Suelo", "Nivel 1", "Nivel 2", "Nivel 3"], width=90, height=28)
        self.combo_nivel_mover.grid(row=1, column=2, padx=2)

        ctk.CTkLabel(panel_reasign, text="Posición", font=ctk.CTkFont(size=10)).grid(row=0, column=3)
        self.entry_pos_mover = ctk.CTkEntry(panel_reasign, width=70, height=28)
        self.entry_pos_mover.grid(row=1, column=3, padx=2)

        self.btn_mover_palet = ctk.CTkButton(panel_reasign, text="✅ Mover a Almacén", width=120, height=28, command=self.mover_palet_desde_camion)
        self.btn_mover_palet.grid(row=1, column=4, columnspan=2, padx=2)

        # Tabla camiones (izquierda)
        ctk.CTkLabel(self.tab_camiones, text="🚚 CAMIONES DISPONIBLES", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="nw", padx=10, pady=10)
        frame_cam = ctk.CTkFrame(self.tab_camiones)
        frame_cam.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        frame_cam.grid_rowconfigure(0, weight=1)
        frame_cam.grid_columnconfigure(0, weight=1)

        self.tree_cam = ttk.Treeview(frame_cam, columns=("ID", "Matrícula", "Chófer", "Palets", "Cap", "Estado"), height=10)
        self.tree_cam.column("#0", width=0)
        for col, width in [("ID", 80), ("Matrícula", 100), ("Chófer", 120), ("Palets", 60), ("Cap", 60), ("Estado", 80)]:
            self.tree_cam.column(col, width=width, anchor="center")
            self.tree_cam.heading(col, text=col)
        self.tree_cam.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_cam.bind("<Double-1>", self.ver_palets_camion)

        # Tabla palets del camión (derecha)
        ctk.CTkLabel(self.tab_camiones, text="📦 PALETS EN CAMIÓN", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, sticky="nw", padx=10, pady=10)
        frame_palets_cam = ctk.CTkFrame(self.tab_camiones)
        frame_palets_cam.grid(row=3, column=1, sticky="nsew", padx=10, pady=(0, 10))
        frame_palets_cam.grid_rowconfigure(0, weight=1)
        frame_palets_cam.grid_columnconfigure(0, weight=1)

        self.tree_palets_cam = ttk.Treeview(frame_palets_cam, columns=("ID", "Producto", "Pasillo", "Nivel", "Pos", "Acción"), height=10)
        self.tree_palets_cam.column("#0", width=0)
        for col, width in [("ID", 80), ("Producto", 150), ("Pasillo", 60), ("Nivel", 80), ("Pos", 50), ("Acción", 80)]:
            self.tree_palets_cam.column(col, width=width, anchor="center")
            self.tree_palets_cam.heading(col, text=col)
        self.tree_palets_cam.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_palets_cam.bind("<Double-1>", self.extraer_palet_camion)

        self.lbl_camion_actual = ctk.CTkLabel(self.tab_camiones, text="Camión: -", font=ctk.CTkFont(size=10))
        self.lbl_camion_actual.grid(row=2, column=1, sticky="ne", padx=10, pady=10)

        self.actualizar_camiones()

    # ========================== MÉTODOS DE ACTUALIZACIÓN ==========================
    def actualizar_acceso(self):
        for tree in [self.tree_pend, self.tree_dentro]:
            for row in tree.get_children():
                tree.delete(row)

        for op in self.sistema.operarios:
            # Aplicar filtro de ETT si existe
            if self.ett_filtrada is not None and op.ett != self.ett_filtrada:
                continue
            
            if op.estado == "PENDIENTE":
                self.tree_pend.insert("", "end", values=(op.id_operario, op.nombre, op.ett, op.turno, op.observacion))
            elif op.estado == "PRESENTE":
                self.tree_dentro.insert("", "end", values=(op.id_operario, op.hora_ingreso, op.nombre, op.ett, op.turno, op.observacion))

    def mostrar_faltantes(self, turno):
        for row in self.tree_faltan.get_children():
            self.tree_faltan.delete(row)
        
        if turno == "Todos":
            faltantes = [op for op in self.sistema.operarios if op.estado == "PENDIENTE"]
        else:
            faltantes = [op for op in self.sistema.operarios if op.estado == "PENDIENTE" and op.turno == turno]
        
        for op in faltantes:
            self.tree_faltan.insert("", "end", values=(op.nombre, op.turno, op.observacion, "Marcar"))

    def actualizar_almacen(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        for prod in self.sistema.inventario:
            reserva = self.sistema.stock_reserva.get(prod.sku, 0)
            self.tree_inv.insert("", "end", values=(prod.sku, prod.nombre, prod.pasillo, prod.nivel, prod.stock, reserva, prod.rotacion))

    def filtrar_inventario(self, event=None):
        """Filtra el inventario por SKU o nombre de producto"""
        busqueda = self.entry_buscar_inv.get().lower()
        
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        
        for prod in self.sistema.inventario:
            if busqueda in prod.sku.lower() or busqueda in prod.nombre.lower():
                reserva = self.sistema.stock_reserva.get(prod.sku, 0)
                self.tree_inv.insert("", "end", values=(prod.sku, prod.nombre, prod.pasillo, prod.nivel, prod.stock, reserva, prod.rotacion))

    def actualizar_camiones(self):
        """Actualiza la tabla de camiones mostrando cantidad de palets"""
        for row in self.tree_cam.get_children():
            self.tree_cam.delete(row)
        for cam in self.sistema.camiones:
            cant_palets = len(cam.palets_asignados)
            self.tree_cam.insert("", "end", values=(cam.id_camion, cam.matricula, cam.chofer, cant_palets, cam.capacidad_palets, cam.estado))

    def actualizar_palets(self):
        """Actualiza la tabla de palets con todos los palets del almacén"""
        for row in self.tree_palets.get_children():
            self.tree_palets.delete(row)
        
        for palet in self.sistema.palets:
            self.tree_palets.insert("", "end", values=(
                palet.id_palet,
                palet.nombre_producto,
                palet.pasillo,
                palet.nivel,
                palet.posicion,
                palet.operario_asignado if palet.operario_asignado else "--",
                palet.estado,
                palet.fecha_ubicacion
            ))
        
        self.lbl_total_palets.configure(text=f"📦 Total: {len(self.sistema.palets)} palets")

    def filtrar_palets(self, event=None):
        """Filtra palets por búsqueda, pasillo y nivel"""
        for row in self.tree_palets.get_children():
            self.tree_palets.delete(row)
        
        busqueda = self.entry_buscar_palet.get().lower()
        pasillo_filtro = self.combo_pasillo.get()
        nivel_filtro = self.combo_nivel.get()
        
        palets_filtrados = self.sistema.palets
        
        if busqueda:
            palets_filtrados = [p for p in palets_filtrados if busqueda in p.id_palet.lower() or busqueda in p.nombre_producto.lower()]
        
        if pasillo_filtro != "Todos":
            palets_filtrados = [p for p in palets_filtrados if p.pasillo == pasillo_filtro]
        
        if nivel_filtro != "Todos":
            palets_filtrados = [p for p in palets_filtrados if p.nivel == nivel_filtro]
        
        for palet in palets_filtrados:
            self.tree_palets.insert("", "end", values=(
                palet.id_palet,
                palet.nombre_producto,
                palet.pasillo,
                palet.nivel,
                palet.posicion,
                palet.operario_asignado if palet.operario_asignado else "--",
                palet.estado,
                palet.fecha_ubicacion
            ))
        
        self.lbl_total_palets.configure(text=f"📦 Mostrados: {len(palets_filtrados)}/{len(self.sistema.palets)}")

    def mover_palet_accion(self):
        """Mueve un palet a una nueva ubicación y lo asigna a un operario"""
        id_palet = self.entry_mover_id.get().strip().upper()
        pasillo = self.combo_pasillo_dest.get()
        nivel = self.combo_nivel_dest.get()
        operario = self.combo_operario.get()
        
        try:
            posicion = int(self.entry_posicion.get())
            if posicion < 1 or posicion > 20:
                messagebox.showwarning("Error", "Posición debe estar entre 1 y 20")
                return
        except:
            messagebox.showwarning("Error", "Posición debe ser un número")
            return
        
        if not id_palet:
            messagebox.showwarning("Error", "Ingresa ID del palet")
            return
        
        # Buscar palet
        palet_encontrado = None
        for p in self.sistema.palets:
            if p.id_palet == id_palet:
                palet_encontrado = p
                break
        
        if not palet_encontrado:
            messagebox.showerror("Error", f"Palet {id_palet} no encontrado")
            return
        
        # Mover palet
        op_asignado = None if operario == "Sin asignar" else operario
        exito = self.sistema.mover_palet(id_palet, pasillo, nivel, posicion, op_asignado)
        
        if exito:
            messagebox.showinfo("✅", f"Palet {id_palet}\n📍 Ubicación: {pasillo}-{nivel}-{posicion}\n👤 Operario: {op_asignado or 'Sin asignar'}")
            self.entry_mover_id.delete(0, 'end')
            self.entry_posicion.delete(0, 'end')
            self.actualizar_palets()
        else:
            messagebox.showerror("Error", "No se pudo mover el palet")

    # ========================== MÉTODOS DE ACCIÓN ==========================
    def _cargar_personas_iniciales(self):
        """Carga automáticamente 30 mañana, 20 tarde, 10 noche distribuidas entre 3 ETTs"""
        etts = ["RANDSTAD", "ADECCO", "MANPOWER"]
        
        # Mañana: 30 personas (10 por ETT)
        for ett in etts:
            for i in range(10):
                op = Operario(
                    id_operario=f"{ett[:3]}-M-{i+1:03d}",
                    nombre=generar_nombre(),
                    dni=generar_dni(),
                    ett=ett,
                    turno="Mañana",
                    salario=round(random.uniform(1200, 2500), 2)
                )
                self.sistema.agregar_operario(op)
        
        # Tarde: 20 personas (6-7 por ETT)
        for idx, ett in enumerate(etts):
            cantidad = 7 if idx < 2 else 6  # 7 + 7 + 6 = 20
            for i in range(cantidad):
                op = Operario(
                    id_operario=f"{ett[:3]}-T-{i+1:03d}",
                    nombre=generar_nombre(),
                    dni=generar_dni(),
                    ett=ett,
                    turno="Tarde",
                    salario=round(random.uniform(1200, 2500), 2)
                )
                self.sistema.agregar_operario(op)
        
        # Noche: 10 personas (3-4 por ETT)
        for idx, ett in enumerate(etts):
            cantidad = 4 if idx < 1 else 3  # 4 + 3 + 3 = 10
            for i in range(cantidad):
                op = Operario(
                    id_operario=f"{ett[:3]}-N-{i+1:03d}",
                    nombre=generar_nombre(),
                    dni=generar_dni(),
                    ett=ett,
                    turno="Noche",
                    salario=round(random.uniform(1200, 2500), 2)
                )
                self.sistema.agregar_operario(op)
        
        self.actualizar_acceso()

    def registrar_persona(self):
        nombre = self.entry_nombre.get().strip()
        dni = self.entry_dni.get().strip()
        ett = self.combo_ett.get()
        turno = self.combo_turno.get()

        if not nombre or not dni:
            messagebox.showwarning("Atención", "Rellena Nombre y DNI")
            return

        op = Operario(id_operario=f"{ett[:3]}-{turno[0]}-{random.randint(1,999):03d}", nombre=nombre, dni=dni, ett=ett, turno=turno)
        exito, msg = self.sistema.agregar_operario(op)

        if exito:
            messagebox.showinfo("✅", f"{nombre} registrado")
            self.entry_nombre.delete(0, 'end')
            self.entry_dni.delete(0, 'end')
            self.actualizar_acceso()
        else:
            messagebox.showerror("❌", msg)

    def filtrar_por_ett(self, ett_filtro):
        """Filtra las tablas de personal por ETT seleccionada"""
        self.ett_filtrada = ett_filtro
        
        # Limpiar tablas
        for tree in [self.tree_pend, self.tree_dentro, self.tree_faltan]:
            for row in tree.get_children():
                tree.delete(row)
        
        # Llenar tabla de pendientes
        for op in self.sistema.operarios:
            if op.estado == "PENDIENTE":
                if self.ett_filtrada is None or op.ett == self.ett_filtrada:
                    self.tree_pend.insert("", "end", values=(op.id_operario, op.nombre, op.turno))
        
        # Llenar tabla de dentro
        for op in self.sistema.operarios:
            if op.estado == "PRESENTE":
                if self.ett_filtrada is None or op.ett == self.ett_filtrada:
                    self.tree_dentro.insert("", "end", values=(op.id_operario, op.nombre, op.hora_ingreso))
        
        # Actualizar título del filtro
        titulo = f"⏳ PENDIENTES (Filtro: {self.ett_filtrada or 'Todos'})" if self.ett_filtrada else "⏳ PENDIENTES (Todos)"
        titulo_dentro = f"🟢 DENTRO (Filtro: {self.ett_filtrada or 'Todos'})" if self.ett_filtrada else "🟢 DENTRO (Todos)"

    def fichar_entrada(self):
        sel = self.tree_pend.selection()
        if not sel:
            return
        id_op = self.tree_pend.item(sel[0])["values"][0]
        for op in self.sistema.operarios:
            if op.id_operario == id_op:
                op.estado = "PRESENTE"
                op.hora_ingreso = datetime.now().strftime("%H:%M:%S")
                messagebox.showinfo("✅ ENTRADA REGISTRADA", f"{op.nombre}\n🕐 Hora: {op.hora_ingreso}\n🏢 ETT: {op.ett}\n📅 Turno: {op.turno}")
                break
        self.actualizar_acceso()

    def fichar_salida(self):
        sel = self.tree_dentro.selection()
        if not sel:
            return
        id_op = self.tree_dentro.item(sel[0])["values"][0]
        for op in self.sistema.operarios:
            if op.id_operario == id_op:
                op.estado = "SALIDO"
                op.hora_salida = datetime.now().strftime("%H:%M:%S")
                messagebox.showinfo("🚪 SALIDA REGISTRADA", f"{op.nombre}\n📥 Entrada: {op.hora_ingreso}\n📤 Salida: {op.hora_salida}\n⏱️ Duración: Calculada")
                break
        self.actualizar_acceso()

    def marcar_falta_seleccionado(self):
        """Marca a una persona como falta con motivo"""
        sel = self.tree_faltan.selection()
        if not sel:
            messagebox.showwarning("Error", "Selecciona una persona de la lista de faltantes")
            return
        
        nombre_falta = self.tree_faltan.item(sel[0])["values"][0]
        motivo = self.entry_obs_falta.get().strip()
        
        if not motivo:
            messagebox.showwarning("Error", "Ingresa un motivo para la falta (Enfermedad, Vacaciones, etc.)")
            return
        
        # Buscar y actualizar operario
        for op in self.sistema.operarios:
            if op.nombre == nombre_falta and op.estado == "PENDIENTE":
                op.observacion = motivo
                op.estado = "AUSENTE"
                op.dias_falta += 1  # Incrementar contador de faltas
                messagebox.showinfo("✅ FALTA REGISTRADA", f"{op.nombre}\n🔴 Motivo: {motivo}\n📅 Turno: {op.turno}\n📊 Faltas: {op.dias_falta}")
                self.entry_obs_falta.delete(0, 'end')
                self.mostrar_faltantes(self.combo_turno_faltan.get())
                break
        else:
            messagebox.showerror("Error", "No se encontró la persona seleccionada")

    def activar_verano(self):
        self.sistema.activar_modo_verano()
        self.actualizar_almacen()
        messagebox.showinfo("☀️", "Modo VERANO activado: productos de alta rotación en Pasillo A - Suelo")

    def activar_invierno(self):
        self.sistema.activar_modo_invierno()
        self.actualizar_almacen()
        messagebox.showinfo("❄️", "Modo INVIERNO activado: reordenación de pasillos")

    def mostrar_alertas(self):
        alertas = self.sistema.obtener_alerta_reposicion()
        if alertas:
            msg = "\n".join(alertas)
            messagebox.showinfo("🔴 Alertas de Reposición", msg)
        else:
            messagebox.showinfo("✅", "Sin alertas de reposición")

    def cargar_foto(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if ruta:
            self.fotos_cargadas.append(ruta)
            self.lbl_fotos.configure(text=f"{len(self.fotos_cargadas)} foto(s)")

    def crear_albarani(self):
        tipo = self.combo_tipo_alb.get()
        producto = self.combo_prod.get()
        try:
            cantidad = int(self.entry_cant.get())
        except:
            messagebox.showwarning("Atención", "Cantidad inválida")
            return

        id_alb = self.sistema.crear_albarani(tipo, producto, cantidad, self.fotos_cargadas)
        messagebox.showinfo("✅", f"Albarani creado: {id_alb}")
        self.entry_cant.delete(0, 'end')
        self.fotos_cargadas = []
        self.lbl_fotos.configure(text="Sin fotos")
        self.actualizar_tab_albaranes()

    def actualizar_tab_albaranes(self):
        for row in self.tree_alb.get_children():
            self.tree_alb.delete(row)
        for alb in self.sistema.albaranes:
            self.tree_alb.insert("", "end", values=(alb.id_albarani, alb.tipo, alb.fecha, alb.producto, alb.cantidad, len(alb.fotos), alb.estado))

    def generar_palets_random(self):
        """Genera una asignación RANDOM de palets a cada camión"""
        for cam in self.sistema.camiones:
            self.sistema.asignar_palets_random_a_camion(cam.id_camion)
        self.actualizar_camiones()
        messagebox.showinfo("✅ Asignación Completada", "Se han asignado palets RANDOM a todos los camiones.\nDoble clic en un camión para ver sus palets.")

    def ver_palets_camion(self, event=None):
        """Muestra los palets de un camión cuando se hace doble clic"""
        seleccion = self.tree_cam.selection()
        if not seleccion:
            return
        
        item = self.tree_cam.item(seleccion[0])
        id_camion = item['values'][0]
        chofer = item['values'][2]
        
        # Limpiar tabla de palets
        for row in self.tree_palets_cam.get_children():
            self.tree_palets_cam.delete(row)
        
        # Cargar palets del camión seleccionado
        palets = self.sistema.obtener_palets_de_camion(id_camion)
        for palet in palets:
            self.tree_palets_cam.insert("", "end", values=(palet.id_palet, palet.nombre_producto, palet.pasillo, palet.nivel, palet.posicion, "Extraer"))
        
        # Actualizar etiqueta
        self.lbl_camion_actual.configure(text=f"Camión: {id_camion} - Chófer: {chofer}")
        
        # Guardar referencia del camión actual
        self.camion_actual = id_camion

    def extraer_palet_camion(self, event=None):
        """Extrae un palet del camión y lo prepara para reasignar en el almacén"""
        if not hasattr(self, 'camion_actual'):
            messagebox.showwarning("⚠️ Advertencia", "Selecciona un camión primero (doble clic).")
            return
        
        seleccion = self.tree_palets_cam.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Advertencia", "Selecciona un palet para extraer.")
            return
        
        item = self.tree_palets_cam.item(seleccion[0])
        id_palet = item['values'][0]
        
        # Extraer el palet del camión
        self.sistema.remover_palet_de_camion(self.camion_actual, id_palet)
        self.tree_palets_cam.delete(seleccion[0])
        
        # Rellenar campos para reasignar
        self.entry_palet_mover.delete(0, tk.END)
        self.entry_palet_mover.insert(0, id_palet)
        
        messagebox.showinfo("✅ Palet Extraído", f"Palet {id_palet} extraído.\nAhora ingresa nueva ubicación y haz clic en 'Mover a Almacén'.")

    def mover_palet_desde_camion(self):
        """Reasigna un palet a una nueva ubicación en el almacén"""
        id_palet = self.entry_palet_mover.get().strip()
        pasillo = self.combo_pasillo_mover.get()
        nivel = self.combo_nivel_mover.get()
        
        try:
            posicion = int(self.entry_pos_mover.get().strip())
        except ValueError:
            messagebox.showerror("❌ Error", "Ingresa una posición válida (número).")
            return
        
        if not id_palet:
            messagebox.showerror("❌ Error", "Ingresa un ID de palet.")
            return
        
        # Reasignar palet
        if self.sistema.reasignar_palet_ubicacion(id_palet, pasillo, nivel, posicion):
            messagebox.showinfo("✅ Reasignación Exitosa", f"Palet {id_palet} movido a:\n📍 Pasillo {pasillo}, {nivel}, Posición {posicion}")
            self.entry_palet_mover.delete(0, tk.END)
            self.entry_pos_mover.delete(0, tk.END)
            self.combo_pasillo_mover.set("A")
            self.combo_nivel_mover.set("Suelo")
            self.actualizar_palets()
        else:
            messagebox.showerror("❌ Error", f"No se encontró el palet {id_palet}.")


# =====================================================================
# ENTRADA PRINCIPAL
# =====================================================================

if __name__ == "__main__":
    sistema = SistemaAlmacen()
    app = DashboardApp(sistema)
    app.mainloop()