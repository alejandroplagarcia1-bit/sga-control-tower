# 📊 SAP ALMACÉN - DISTRIBUIDORA DE REPOSTERÍA

## 🎯 Sistema Completo de Gestión - Versión Mejorada 2.0

Sistema integral para distribuidoras de productos de repostería y pastelería con control de acceso, gestión de palets, albaranes y flota.

---

## 🚪 **MÓDULO 1: CONTROL DE ACCESO & TURNOS**

### ✨ Nuevas Características

#### 📋 **Carga Automática**

- ✅ **60 Operarios precargados** al iniciar la aplicación:
  - Mañana: 10 RANDSTAD + 10 ADECCO + 10 MANPOWER = 30
  - Tarde: 7 RANDSTAD + 6 ADECCO + 7 MANPOWER = 20
  - Noche: 3 RANDSTAD + 4 ADECCO + 3 MANPOWER = 10

#### 🏢 **Filtros por ETT**

- 🔵 Botón **RANDSTAD** - Ver solo empleados RANDSTAD
- 🟠 Botón **ADECCO** - Ver solo empleados ADECCO
- 🟣 Botón **MANPOWER** - Ver solo empleados MANPOWER
- 🟢 Botón **Ver Todos** - Mostrar todas las ETTs

#### 📊 **Tabla: PENDIENTES DE ENTRAR**

| ID         | Nombre      | ETT      | Turno  | Observación |
| ---------- | ----------- | -------- | ------ | ----------- |
| RAND-M-001 | Juan García | RANDSTAD | Mañana | -           |

**Acción**: Doble clic = Registrar entrada + Hora exacta

#### 🟢 **Tabla: DENTRO DEL ALMACÉN**

| ID         | Entrada  | Nombre      | ETT      | Turno  | Observación |
| ---------- | -------- | ----------- | -------- | ------ | ----------- |
| RAND-M-001 | 07:45:32 | Juan García | RANDSTAD | Mañana | -           |

**Acción**: Doble clic = Registrar salida + Hora exacta

#### ❌ **Tabla: FALTANTES HOY**

- **Selector de Turno**: Mañana / Tarde / Noche / Todos
- **Campo Motivo**: Enfermedad, Vacaciones, Permisos, etc.
- **Acciones**:
  - Ver quién falta en cada turno
  - Doble clic = Marcar falta con motivo

| Nombre      | Turno  | Motivo     | Acción |
| ----------- | ------ | ---------- | ------ |
| María López | Mañana | Enfermedad | Marcar |

---

## 📦 **MÓDULO 2: GESTIÓN DE ALMACÉN**

### 🏭 **Productos de Repostería (60 tipos)**

#### Categorías principales:

- **HARINAS** (4): Trigo, Integral, Pastelera, Maíz
- **AZÚCARES** (4): Blanco, Moreno, Glas, Moscovado
- **GRASAS** (5): Mantequilla Pura, Vegana, Aceite Oliva, Girasol, Margarina
- **LEVADURA** (4): Fresca, Seca, Polvo Hornear, Bicarbonato
- **CHOCOLATE** (5): Negro, Leche, Blanco, Cacao Polvo, Virutas
- **FRUTAS SECAS** (6): Pasas, Arándanos, Nueces, Almendras, Ciruelas, Coco
- **ESENCIAS** (5): Vainilla, Almendra, Ron, Naranja, Limón
- **LÁCTEOS** (4): Leche en Polvo, Crema, Mascarpone, Yogur
- **COBERTURAS** (5): Fondant, Perlas, Mentas, Cajas, Glaseado
- **ESPECIAS** (5): Canela, Nuez Moscada, Ajonjolí, Pimienta, Clavo
- **BEBIDAS** (4): Café, Té, Agua, Refresco
- **MOLDES** (4): Cake, Donuts, Bandejas, Papel Hornear
- **COLORANTES** (3): Colorante, Gelatina, Almidón

### 🔍 **Buscador de Inventario**

- Campo de búsqueda por **SKU** o **Nombre del producto**
- Búsqueda en tiempo real (teclea y se filtra automáticamente)
- Ejemplo: "Harina" busca todas las harinas

### 🎨 **Modos Estacionales**

- ☀️ **VERANO**: Productos de alta rotación → Pasillo A (acceso rápido)
- ❄️ **INVIERNO**: Reordenación según demanda estacional
- 🔴 **VER ALERTAS**: Notificaciones de stock bajo

---

## 📍 **MÓDULO 3: PALETS & UBICACIONES**

### 🎯 **Sistema de Gestión de Palets**

#### 📊 **Total: 92 Palets**

- Distribuidos en **Pasillos A-J**
- Cuatro niveles cada pasillo:
  - Suelo (Picking rápido)
  - Nivel 1
  - Nivel 2
  - Nivel 3 (Reserva)

#### 🔍 **Filtros Avanzados**

- Buscar por **ID de Palet** (PAL-00001)
- Filtrar por **Pasillo** (A-J)
- Filtrar por **Nivel** (Suelo, N1, N2, N3)

#### 📍 **Mover Palets**

1. Ingresar **ID del Palet**
2. Seleccionar **Pasillo destino**
3. Seleccionar **Nivel destino**
4. Ingresar **Posición** (1-20)
5. Asignar a **Operario** (Si es necesario)
6. Clic en **✅ MOVER**

Resultado: Se registra la reubicación con fecha/hora

#### 📋 **Tabla de Palets**

| ID        | Producto        | Pasillo | Nivel | Pos | Operario   | Estado  | Fecha            |
| --------- | --------------- | ------- | ----- | --- | ---------- | ------- | ---------------- |
| PAL-00001 | Harina de Trigo | A       | Suelo | 5   | RAND-M-001 | ubicado | 14/08/2024 10:30 |

**Acciones**:

- Ver estado actual de cada palet
- Historial de ubicación
- Operario asignado

---

## 📋 **MÓDULO 4: ALBARANES**

### 📦 **Tipos de Albaranes**

1. **Entrega** ✈️ - Producto que sale del almacén
2. **Recogida** 🔄 - Devoluciones/Recogidas
3. **Entrada** 📥 - Mercancía que llega

### 🎯 **Crear Albarani**

1. Seleccionar **Tipo** (entrega/recogida/entrada)
2. Elegir **Producto** de lista desplegable
3. Ingresar **Cantidad**
4. **Opcional**: Cargar **fotos** (📸)
   - Múltiples imágenes por albarani
   - Verificación visual de mercancía
5. Clic en **✅ Crear Albarani**

### 📊 **Tabla de Albaranes**

| ID        | Tipo    | Fecha       | Producto        | Cantidad | Fotos | Estado    |
| --------- | ------- | ----------- | --------------- | -------- | ----- | --------- |
| ALB-00001 | entrega | 14/08 09:15 | Harina de Trigo | 5        | 2     | pendiente |

---

## 🚚 **MÓDULO 5: FLOTA DE CAMIONES**

### 🚛 **4 Camiones Disponibles**

#### Información por Camión:

- **ID**: CAM-001, CAM-002, CAM-003, CAM-004
- **Matrícula**: Autogenerada (ej: 5234AB)
- **Chófer**: Nombre completo
- **DNI Chófer**: Documento de identidad
- **Capacidad**: 20-30 palets
- **Estado**: Disponible / Ocupado

#### 📊 **Tabla de Flota**

| ID      | Matrícula | Chófer       | DNI       | Capacidad | Estado     |
| ------- | --------- | ------------ | --------- | --------- | ---------- |
| CAM-001 | 5234AB    | Carlos López | 12345678X | 25        | disponible |

---

## 🎮 **CÓMO USAR LA APLICACIÓN**

### Paso 1️⃣: Iniciar Sesión

- Ejecutar: `python main.py`
- Sistema carga automáticamente:
  - ✅ 60 operarios (3 ETTs × 3 turnos)
  - ✅ 92 palets distribuidos
  - ✅ 4 camiones con chóferes

### Paso 2️⃣: Gestionar Acceso (Pestaña 🚪)

```
1. Ver PENDIENTES → Doble clic → FICHAR ENTRADA
2. Ver DENTRO → Doble clic → FICHAR SALIDA
3. Ver FALTANTES → Marcar ausencias con motivo
4. Filtrar por ETT usando botones de colores
```

### Paso 3️⃣: Gestionar Palets (Pestaña 📍)

```
1. Buscar palet por ID
2. Filtrar por pasillo y nivel
3. Mover a nueva ubicación
4. Asignar a operario si es necesario
```

### Paso 4️⃣: Crear Albaranes (Pestaña 📋)

```
1. Seleccionar tipo (entrega/recogida/entrada)
2. Elegir producto y cantidad
3. Cargar fotos (opcional)
4. Crear albarani
```

### Paso 5️⃣: Ver Flota (Pestaña 🚚)

```
1. Clic "🎲 Generar Asignación Random" = Asignar palets RANDOM a cada camión
2. Doble clic en un camión = Ver palets que lleva
3. Doble clic en un palet = Extraerlo del camión
4. Ingresar nueva Pasillo/Nivel/Posición
5. Clic "✅ Mover a Almacén" = Reasignar palet en el almacén
```

### Paso 6️⃣: Descargar Personal (Pestaña 📦 Almacén)

```
1. Clic "📥 Descargar Personal" → Se abre archivo Excel
2. Excel contiene:
   - ID, Nombre, DNI, ETT, Turno
   - Salario (€) - Salario mensual de cada operario
   - Entrada - Hora exacta de entrada
   - Salida - Hora exacta de salida
   - Estado - PENDIENTE/PRESENTE/SALIDO/AUSENTE
   - En Baja - SÍ/NO
   - Días Falta - Total de días faltados
   - Motivo - Razón de la falta (Enfermedad, Vacaciones, etc.)
```

---

## 📥 **NÓMINA DE PERSONAL**

### 📋 **Estructura de Descarga**

El archivo `personal_control.xlsx` incluye:

| Columna         | Descripción                       |
| --------------- | --------------------------------- |
| ID              | Identificador único del operario  |
| Nombre          | Nombre completo                   |
| DNI             | Documento de identidad            |
| ETT             | Empresa de Trabajo Temporal       |
| Turno           | Mañana / Tarde / Noche            |
| **Salario (€)** | Salario mensual (1.200 - 2.500 €) |
| Entrada         | Hora de entrada (HH:MM:SS)        |
| Salida          | Hora de salida (HH:MM:SS)         |
| Estado          | PENDIENTE/PRESENTE/SALIDO/AUSENTE |
| **En Baja**     | SÍ = En baja, NO = Trabajando     |
| **Días Falta**  | Contador de días faltados         |
| **Motivo**      | Razón de la falta o evento        |

### 💼 **Salarios Precargados**

- **Rango**: 1.200 € a 2.500 € mensuales
- **Asignación**: ALEATORIA para cada operario
- **Actualización**: Los salarios se generan al iniciar la aplicación

### 📊 **Control de Bajas**

1. **Cada falta registrada** incrementa el contador "Días Falta"
2. **En Baja = SÍ** cuando el operario está marcado como AUSENTE
3. **Motivo** se guarda automáticamente:
   - Enfermedad
   - Vacaciones
   - Permisos
   - Otros eventos

### 📈 **Cálculos Disponibles en Excel**

Puedes agregar fórmulas en Excel para:

- **Descuento por faltas**: `(Días_Falta / 22) * Salario`
- **Nómina neta**: `Salario - Descuentos`
- **Horas trabajadas**: Calculadas desde Entrada y Salida
- **Totales por ETT**: Usando SUMIF()

---

## 📊 **Datos Precargados**

### Operarios por ETT y Turno

```
MAÑANA (30):
  • 10 de RANDSTAD
  • 10 de ADECCO
  • 10 de MANPOWER

TARDE (20):
  • 7 de RANDSTAD
  • 6 de ADECCO
  • 7 de MANPOWER

NOCHE (10):
  • 3 de RANDSTAD
  • 4 de ADECCO
  • 3 de MANPOWER
```

### Pasillos y Niveles

```
Pasillos A-H: Picking Activo (volumen normal)
Pasillos I-J: Reserva/Sobrestock (volumen alto)

Niveles por Pasillo:
  • Suelo: Acceso más rápido (picking)
  • Nivel 1: Acceso medio
  • Nivel 2: Acceso medio-alto
  • Nivel 3: Acceso lento (reserva)
```

---

## 🔄 **Flujo de Trabajo Típico**

### Mañana (07:00)

1. Clic en botón **RANDSTAD** → Ver solo operarios RANDSTAD
2. Doble clic en cada persona → Fichar entrada automática
3. Sistema registra: Nombre, Hora exacta, ETT, Turno

### Durante el turno

1. Pestaña **Palets** → Mover palets a ubicaciones
2. Asignar a operarios presentes
3. Registrar cambios de ubicación

### Salida (15:00)

1. Ver tabla **DENTRO**
2. Doble clic en cada persona → Fichar salida
3. Sistema registra hora de salida

### Gestionar Faltas

1. Pestaña **Acceso** → Panel de Faltantes
2. Seleccionar turno
3. Ingresar motivo (Enfermedad, Vacaciones)
4. Doble clic en faltante → Marcar

### Enviar Pedidos

1. Pestaña **Albaranes**
2. Crear albarani de entrega
3. Adjuntar fotos de los palets
4. Asignar a camión de flota

### Gestionar Nómina (Fin de Mes)

1. Pestaña **Almacén** → Botón "📥 Descargar Personal"
2. Se abre Excel con datos completos:
   - Salarios
   - Horas de entrada/salida
   - Días faltados
   - Motivos de faltas
3. Aplicar descuentos por faltas
4. Calcular nómina neta
5. Generar recibos

### Gestionar Flota (Envíos)

1. Pestaña **Flota** → Botón "🎲 Generar Asignación Random"
2. Cada camión recibe palets RANDOM
3. Doble clic en camión = Ver palets asignados
4. Doble clic en palet = Extraerlo
5. Reasignar a nueva ubicación en almacén
6. Cada carga es diferente (generada al azar)

---

## 🛠️ **Instalación y Requisitos**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### Dependencias:

- customtkinter >= 5.2.0
- pandas >= 2.0.0
- pymongo >= 4.5.0 (opcional)
- openpyxl >= 3.1.0
- pillow >= 10.0.0

---

## 💡 **Tips de Uso**

✅ **Los datos se cargan automáticamente** - No necesitas hacer nada al iniciar
✅ **Haz clic rápido dos veces para fichar** - En las tablas de PENDIENTES y DENTRO
✅ **Usa los filtros de ETT** - Para ver solo los operarios que necesitas
✅ **Las horas se registran automáticamente** - Con precisión a segundos
✅ **Las observaciones se guardan** - Para justificar faltas o eventos
✅ **Busca palets rápidamente** - Por ID en la pestaña de Palets
✅ **Exporta nóminas a Excel** - Botón en la pestaña Almacén

---

## 🎨 **Colores y Significados**

| Color       | Significado       |
| ----------- | ----------------- |
| 🟦 Azul     | RANDSTAD          |
| 🟧 Naranja  | ADECCO            |
| 🟪 Morado   | MANPOWER          |
| 🟢 Verde    | Dentro/Disponible |
| 🟡 Amarillo | Pendiente         |
| 🔴 Rojo     | Falta/Problema    |

---

## 📝 **Notas Importantes**

- Cada persona tiene un **ID único** (ETT-Turno-Número)
- Las **horas se registran automáticamente** cuando fichás entrada/salida
- Las **observaciones se guardan** para cada operario
- Los **palets tienen ubicación precisa** (Pasillo-Nivel-Posición)
- Los **albaranes incluyen fecha/hora** de creación
- El **sistema es en tiempo real** - Los datos se actualizan al instante

---

**Desarrollado para empresa distribuidora de Repostería y Pastelería** 🧁🎂

Última actualización: 14/08/2024 v2.0
