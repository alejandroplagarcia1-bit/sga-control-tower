# 📦 SAP ALMACÉN - Sistema de Control Total

Sistema integral de gestión de almacén con control de acceso, gestión de stock, albaranes y flota de camiones.

## 🎯 Funcionalidades Principales

### 🚪 **Control de Acceso & Turnos**

- Registro individual de operarios
- Carga masiva de ETTs (RANDSTAD, ADECCO, MANPOWER)
- Fichaje de entrada/salida (doble clic)
- **Panel de Faltantes**: Visualiza quién falta por turno (Mañana, Tarde, Noche) con desplegable
- KPIs en tiempo real
- Exportación a Excel de nóminas

### 📦 **Gestión de Almacén**

- **Inventario Activo**: 11 productos clasificados (Bebidas, Harinas, Azúcares, etc.)
- **Stock de Reserva**: Pasillos I y J como amortiguador de volúmenes
- **Modos Estacionales**:
  - ☀️ **Verano**: Productos de alta rotación en Pasillo A (acceso rápido)
  - ❄️ **Invierno**: Reorganización de pasillos según demanda
- **Alertas de Reposición**: Notificaciones automáticas cuando baja stock
- **Pasillos Dinámicos**: A-H (picking activos) + I-J (reserva)

### 📋 **Gestión de Albaranes**

- Crear albaranes de:
  - ✈️ **Entrega**: Salida de productos
  - 🔄 **Recogida**: Entrada de devoluciones
  - 📥 **Entrada**: Control de mercancía que llega
- **Carga de Fotos**: Adjunta imágenes a cada albarani
- Seguimiento de estado

### 🚚 **Flota de Camiones**

- Gestión de 4 camiones
- Datos del chófer (nombre, DNI)
- Matrícula y capacidad de palets
- Estado disponible/ocupado
- Reasignación dinámica

## 📝 **Productos del Almacén**

| SKU       | Producto           | Rotación |
| --------- | ------------------ | -------- |
| FANT-NAR  | Fanta Naranja      | Alta     |
| FANT-LIM  | Fanta Limón        | Alta     |
| COCA-001  | Coca-Cola          | Alta     |
| AGUA-001  | Agua               | Alta     |
| HARINA-01 | Harina             | Media    |
| AZUC-MOR  | Azúcar Moreno      | Media    |
| AZUC-NOR  | Azúcar Normal      | Media    |
| SAL-001   | Sal                | Baja     |
| CACAO-POL | Cacao en Polvo     | Media    |
| CHIP-CAC  | Chispitas de Cacao | Baja     |
| LEVAD-001 | Levadura           | Baja     |

## 🚀 Instalación

```bash
pip install -r requirements.txt
python main.py
```

## 📊 Flujo de Uso

### Control de Acceso

1. **Registrar individuales**: Rellenar datos + seleccionar turno → Registrar
2. **Cargar ETTs completas**: Botones de carga masiva (RANDSTAD, ADECCO, MANPOWER)
3. **Fichaje**: Doble clic en tabla "Pendientes" → Pasa a "Dentro"
4. **Salida**: Doble clic en tabla "Dentro" → Registra hora de salida

### Gestión de Almacén

1. **Ver Inventario**: Pestaña "Almacén" → Tabla con ubicación actual
2. **Cambiar Modo**: Botones "Verano" o "Invierno" → Reorganiza pasillos
3. **Verificar Alertas**: Botón "Ver Alertas" → Notificaciones de reposición

### Albaranes

1. Seleccionar tipo (entrega/recogida/entrada)
2. Elegir producto del inventario
3. Ingresar cantidad
4. **Opcional**: Cargar fotos (📸 Añadir Foto)
5. Crear albarani → Se registra con ID único

### Flota de Camiones

1. Visualizar camiones disponibles
2. Ver datos: matrícula, chófer, capacidad
3. Reasignar según necesidades (próximas versiones)

## ⚙️ Configuración

### Base de Datos

- **Predeterminado**: Memoria local (modo pruebas)
- **Con MongoDB**: Conecta automáticamente si está disponible en `mongodb://localhost:27017/`

### Temas

- Tema oscuro por defecto
- Color azul principal

## 📈 Próximas Mejoras

- [ ] Drag & Drop para mover palets
- [ ] Integración con sistema de picking
- [ ] Gráficos de rotación de stock
- [ ] Reportes avanzados de albaranes
- [ ] Asignación automática de camiones

---

**Desarrollado para ALMACÉN SAP - Control Total** ✨
