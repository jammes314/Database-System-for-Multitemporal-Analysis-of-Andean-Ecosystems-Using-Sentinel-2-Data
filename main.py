from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
import os
from fastapi.middleware.cors import CORSMiddleware # 1. Add this import

app = FastAPI(
    title="Eco Monitoring API",
    description="Full CRUD for eco_monitoring_db — all 7 tables",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "eco_monitoring_db"),
    "user": os.getenv("DB_USER", "api_user"),
    "password": os.getenv("DB_PASSWORD", "apipassword"),
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

def row_to_dict(cursor, row) -> dict:
    return dict(zip([col[0] for col in cursor.description], row))

def rows_to_list(cursor) -> list:
    return [row_to_dict(cursor, r) for r in cursor.fetchall()]

def fk_msg(e) -> str:
    from mysql.connector import Error
    if hasattr(e, 'errno') and e.errno == 1451:
        s = str(e)
        if "registros_monitoreo" in s and "especie_id" in s:
            return "No se puede eliminar: esta especie tiene Registros de Monitoreo asociados. Elimina primero los registros en la tabla Registros."
        if "observaciones_espectrales" in s and "imagen_id" in s:
            return "No se puede eliminar: esta imagen tiene Observaciones Espectrales asociadas. Elimina primero las observaciones."
        if "observaciones_espectrales" in s and "punto_id" in s:
            return "No se puede eliminar: este punto tiene Observaciones o Registros asociados. Elimina primero los registros hijos."
        if "puntos_muestreo" in s:
            return "No se puede eliminar: esta area tiene Puntos de Muestreo. Elimina primero los puntos."
        return "No se puede eliminar: existen registros dependientes en otras tablas. Elimina primero los registros hijos."
    return str(e)




# ══════════════════════════════════════════════════════════════════════════════
#  HEALTH
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "api": "Eco Monitoring API v2.0", "tables": 7}




# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE SERVER — serves PNG files from local images folder
# ══════════════════════════════════════════════════════════════════════════════

from fastapi.responses import FileResponse

IMAGES_DIR = os.getenv("IMAGES_DIR", "/home/jammes/Desktop/dbFinalProject/Images")

@app.get("/images/{image_id}", tags=["Images"])
def get_image(image_id: str):
    """Serve a PNG image by ID (filename without extension)."""
    path = os.path.join(IMAGES_DIR, f"{image_id}.png")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Image '{image_id}.png' not found in {IMAGES_DIR}")
    return FileResponse(path, media_type="image/png")

@app.get("/images", tags=["Images"])
def list_images():
    """List all available PNG image IDs in the images folder."""
    if not os.path.isdir(IMAGES_DIR):
        return {"images": [], "path": IMAGES_DIR, "error": "Directory not found"}
    ids = [f[:-4] for f in os.listdir(IMAGES_DIR) if f.endswith('.png')]
    ids.sort()
    return {"images": ids, "count": len(ids), "path": IMAGES_DIR}

# ══════════════════════════════════════════════════════════════════════════════
#  SEED  — loads rich demo data into all 7 tables in dependency order
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/seed", status_code=201, tags=["Seed"])
def seed_data():
    areas = [
        (1,  "Zona Norte",         "POLYGON((0 0,1 0,1 1,0 1,0 0))", 1),
        (2,  "Zona Sur",           "POLYGON((1 0,2 0,2 1,1 1,1 0))", 2),
        (3,  "Zona Este",          "POLYGON((2 0,3 0,3 1,2 1,2 0))", 1),
        (4,  "Zona Oeste",         "POLYGON((3 0,4 0,4 1,3 1,3 0))", 3),
        (5,  "Zona Central",       "POLYGON((1 1,2 1,2 2,1 2,1 1))", 2),
        (6,  "Reserva Alta",       "POLYGON((0 2,1 2,1 3,0 3,0 2))", 1),
        (7,  "Corredor Fluvial",   "POLYGON((2 2,3 2,3 3,2 3,2 2))", 2),
        (8,  "Bosque Primario",    "POLYGON((4 0,5 0,5 1,4 1,4 0))", 1),
    ]
    biomas = [
        (1, "Bosque Tropical",  "Ecosistema de alta biodiversidad con lluvias superiores a 2000mm anuales."),
        (2, "Paramo",           "Ecosistema de alta montana, reservorio hidrico clave para los Andes."),
        (3, "Manglar",          "Bosque costero en zonas intermareales, habitat de especies marinas."),
        (4, "Bosque Seco",      "Ecosistema con marcada estacionalidad hidrica y alta endemicidad."),
        (5, "Sabana",           "Pastizales tropicales con arboles dispersos, alta productividad primaria."),
        (6, "Bosque Nublado",   "Ecosistema de transicion andina con alta humedad y epifitismo."),
        (7, "Humedal",          "Zona de transicion acuatica-terrestre, regulador hidrologico esencial."),
        (8, "Matorral Andino",  "Vegetacion arbustiva de zonas altoandinas por encima de los 3000msnm."),
    ]
    especies = [
        (1,  "Panthera onca",          "VU"),
        (2,  "Tapirus terrestris",      "VU"),
        (3,  "Ara macao",               "LC"),
        (4,  "Chelonoidis nigra",       "VU"),
        (5,  "Tremarctos ornatus",      "VU"),
        (6,  "Harpia harpyja",          "VU"),
        (7,  "Atelopus ignescens",      "CR"),
        (8,  "Lontra longicaudis",      "NT"),
        (9,  "Vultur gryphus",          "NT"),
        (10, "Podocnemis expansa",      "VU"),
        (11, "Tapirus pinchaque",       "EN"),
        (12, "Lagothrix lagothricha",   "VU"),
        (13, "Crocodylus acutus",       "VU"),
        (14, "Puma concolor",           "LC"),
        (15, "Priodontes maximus",      "VU"),
    ]
    imagenes = [
        ("S2A_20240115_001", "2024-01-15 10:30:00", 5.20,  "Sentinel-2A"),
        ("S2B_20240210_002", "2024-02-10 10:45:00", 12.50, "Sentinel-2B"),
        ("S2A_20240318_003", "2024-03-18 11:00:00", 0.00,  "Sentinel-2A"),
        ("S2B_20240405_004", "2024-04-05 10:20:00", 8.75,  "Sentinel-2B"),
        ("S2A_20240520_005", "2024-05-20 10:55:00", 22.30, "Sentinel-2A"),
        ("S2B_20240612_006", "2024-06-12 11:10:00", 3.10,  "Sentinel-2B"),
        ("S2A_20240728_007", "2024-07-28 10:35:00", 0.50,  "Sentinel-2A"),
        ("S2B_20240814_008", "2024-08-14 10:50:00", 15.60, "Sentinel-2B"),
        ("S2A_20240922_009", "2024-09-22 11:05:00", 6.40,  "Sentinel-2A"),
        ("S2B_20241010_010", "2024-10-10 10:25:00", 1.20,  "Sentinel-2B"),
    ]
    puntos = [
        (1,  1, -0.22985600,  -78.52495800, 2850.00, "hash_p01"),
        (2,  1, -0.23100000,  -78.52600000, 2870.00, "hash_p02"),
        (3,  2, -0.24500000,  -78.53000000, 2900.00, "hash_p03"),
        (4,  2, -0.24700000,  -78.53200000, 2920.00, "hash_p04"),
        (5,  3, -0.21000000,  -78.51000000, 2800.00, "hash_p05"),
        (6,  3, -0.21200000,  -78.51200000, 2810.00, "hash_p06"),
        (7,  4, -0.25000000,  -78.54000000, 2950.00, "hash_p07"),
        (8,  4, -0.25200000,  -78.54200000, 2960.00, "hash_p08"),
        (9,  5, -0.23000000,  -78.52000000, 2840.00, "hash_p09"),
        (10, 5, -0.23100000,  -78.52100000, 2845.00, "hash_p10"),
        (11, 6, -0.20000000,  -78.50000000, 3100.00, "hash_p11"),
        (12, 6, -0.20200000,  -78.50200000, 3120.00, "hash_p12"),
        (13, 7, -0.26000000,  -78.55000000, 2750.00, "hash_p13"),
        (14, 7, -0.26200000,  -78.55200000, 2760.00, "hash_p14"),
        (15, 8, -0.19000000,  -78.49000000, 3200.00, "hash_p15"),
    ]
    observaciones = [
        # (punto_id, imagen_id, b2, b3, b4, b8, b11, b12, ndvi, ndmi, bsi, clase_id, verdad_campo, confianza)
        (1,  "S2A_20240115_001", 520,  780,  430,  3200, 1100, 650,  0.760422, 0.488372, -0.321500, 2, 1, 97.50),
        (2,  "S2A_20240115_001", 610,  850,  520,  2900, 1300, 780,  0.695122, 0.380952, -0.290100, 2, 1, 95.20),
        (3,  "S2B_20240210_002", 480,  720,  390,  3400, 980,  580,  0.795918, 0.553191, -0.348200, 1, 0, 88.70),
        (4,  "S2B_20240210_002", 550,  800,  460,  3100, 1050, 620,  0.743590, 0.493827, -0.310400, 1, 1, 92.30),
        (5,  "S2A_20240318_003", 490,  740,  410,  3300, 1020, 600,  0.778626, 0.529412, -0.335600, 2, 1, 96.10),
        (6,  "S2A_20240318_003", 630,  880,  540,  2800, 1400, 820,  0.675926, 0.333333, -0.275300, 3, 0, 79.40),
        (7,  "S2B_20240405_004", 500,  750,  420,  3250, 1080, 640,  0.770833, 0.503650, -0.328900, 2, 1, 94.80),
        (8,  "S2B_20240405_004", 580,  830,  490,  3000, 1180, 700,  0.719512, 0.432432, -0.301200, 1, 0, 85.60),
        (9,  "S2A_20240520_005", 510,  760,  440,  3150, 1090, 660,  0.755319, 0.483945, -0.318700, 2, 1, 93.40),
        (10, "S2A_20240520_005", 595,  845,  505,  2950, 1220, 720,  0.707921, 0.413534, -0.296800, 1, 1, 91.70),
        (11, "S2B_20240612_006", 470,  710,  380,  3450, 960,  570,  0.802920, 0.563910, -0.352400, 2, 1, 98.20),
        (12, "S2B_20240612_006", 525,  775,  435,  3180, 1110, 655,  0.757143, 0.487805, -0.320100, 2, 0, 87.30),
        (13, "S2A_20240728_007", 560,  815,  470,  3050, 1150, 680,  0.730570, 0.453608, -0.306500, 1, 1, 90.50),
        (14, "S2A_20240728_007", 615,  860,  525,  2880, 1320, 790,  0.692308, 0.373626, -0.287600, 3, 0, 76.80),
        (15, "S2B_20240814_008", 485,  730,  400,  3350, 1000, 590,  0.787879, 0.540984, -0.341800, 2, 1, 95.90),
    ]
    registros = [
        # (especie_id, punto_id, fecha, cantidad, notas)
        (1,  1,  "2024-01-20 08:00:00", 2,  "Huellas frescas y marcas de garras en arboles proximos al punto."),
        (2,  2,  "2024-01-22 09:30:00", 1,  "Individuo adulto observado bebiendo agua en quebrada adyacente."),
        (3,  3,  "2024-02-05 07:15:00", 5,  "Grupo de guacamayas sobrevolando el dosel del bosque primario."),
        (5,  4,  "2024-02-18 10:00:00", 1,  "Oso de anteojos macho adulto alimentandose de bromelias."),
        (6,  5,  "2024-03-01 06:45:00", 1,  "Aguila harpia avistada en vuelo rasante sobre la copa de los arboles."),
        (7,  6,  "2024-03-15 08:30:00", 3,  "Tres individuos de rana cohete observados en zona de quebrada."),
        (8,  7,  "2024-04-02 09:00:00", 2,  "Par de nutrias jugando en el margen del rio principal."),
        (9,  8,  "2024-04-20 11:00:00", 4,  "Grupo de condores andinos planeando sobre la cresta del cerro."),
        (10, 9,  "2024-05-10 07:30:00", 8,  "Charapa adulta con nido activo en playa fluvial de la zona."),
        (11, 10, "2024-05-25 09:45:00", 1,  "Tapir de montania avistado en camino de fauna a 3100msnm."),
        (12, 11, "2024-06-08 08:15:00", 6,  "Tropa de churuco moviendose en el dosel, con juveniles visibles."),
        (14, 12, "2024-06-22 10:30:00", 1,  "Puma fotografiado por camara trampa, activo en horario diurno."),
        (4,  13, "2024-07-05 08:00:00", 3,  "Tres tortugas galapago de la subespecie chathamensis en rio."),
        (15, 14, "2024-07-19 09:15:00", 1,  "Armadillo gigante con evidencia de madriguera activa en el sitio."),
        (13, 15, "2024-08-03 07:00:00", 2,  "Dos cocodrilos americanos asoleandose en orilla del rio."),
        (1,  5,  "2024-08-17 08:45:00", 1,  "Jaguar hembra con cachorros detectada por camara trampa nocturna."),
        (3,  7,  "2024-09-01 06:30:00", 12, "Bandada mixta con guacamayas rojas y verdes en frutal nativo."),
        (6,  9,  "2024-09-14 07:00:00", 2,  "Pareja de aguilas harpia con nido activo en arbol emergente."),
        (9,  11, "2024-10-02 10:00:00", 7,  "Colonia de condores en termal, incluyendo tres juveniles."),
        (2,  13, "2024-10-18 09:30:00", 2,  "Par de dantas de tierras bajas en saladero mineral del bosque."),
    ]

    conn = get_connection()
    cursor = conn.cursor()
    counts = {t: 0 for t in ["areas_acha","catalogo_biomas","especies","catalogo_imagenes","puntos_muestreo","observaciones_espectrales","registros_monitoreo"]}

    def upsert(sql, rows, table):
        """INSERT ... ON DUPLICATE KEY UPDATE — inserts new rows, updates existing ones."""
        for row in rows:
            cursor.execute(sql, row)   # ON DUPLICATE KEY UPDATE uses VALUES(...), so only one parameter set is needed
            counts[table] += 1

    try:
        upsert("""INSERT INTO areas_acha (id,nombre,geometria_poligonal,prioridad_muestreo) VALUES (%s,%s,%s,%s)
                  ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), geometria_poligonal=VALUES(geometria_poligonal), prioridad_muestreo=VALUES(prioridad_muestreo)""",
               areas, "areas_acha")
        upsert("""INSERT INTO catalogo_biomas (id,nombre_clase,descripcion_ecologica) VALUES (%s,%s,%s)
                  ON DUPLICATE KEY UPDATE nombre_clase=VALUES(nombre_clase), descripcion_ecologica=VALUES(descripcion_ecologica)""",
               biomas, "catalogo_biomas")
        upsert("""INSERT INTO especies (id,nombre_cientifico,estado_uicn) VALUES (%s,%s,%s)
                  ON DUPLICATE KEY UPDATE nombre_cientifico=VALUES(nombre_cientifico), estado_uicn=VALUES(estado_uicn)""",
               especies, "especies")
        upsert("""INSERT INTO catalogo_imagenes (id_producto,fecha_adquisicion,porcentaje_nubes,sensor) VALUES (%s,%s,%s,%s)
                  ON DUPLICATE KEY UPDATE fecha_adquisicion=VALUES(fecha_adquisicion), porcentaje_nubes=VALUES(porcentaje_nubes), sensor=VALUES(sensor)""",
               imagenes, "catalogo_imagenes")
        upsert("""INSERT INTO puntos_muestreo (id,area_id,latitud,longitud,altitud,pixel_id_hash) VALUES (%s,%s,%s,%s,%s,%s)
                  ON DUPLICATE KEY UPDATE area_id=VALUES(area_id), latitud=VALUES(latitud), longitud=VALUES(longitud), altitud=VALUES(altitud), pixel_id_hash=VALUES(pixel_id_hash)""",
               puntos, "puntos_muestreo")
        # observaciones uses AUTO_INCREMENT — use REPLACE to avoid duplicates on re-seed
        # We truncate and re-insert to keep data clean on every seed call
        cursor.execute("DELETE FROM registros_monitoreo")
        cursor.execute("DELETE FROM observaciones_espectrales")
        # Reset AUTO_INCREMENT so seeded register IDs match image filenames: 1.png, 2.png, ...
        cursor.execute("ALTER TABLE observaciones_espectrales AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE registros_monitoreo AUTO_INCREMENT = 1")
        for row in observaciones:
            cursor.execute("""INSERT INTO observaciones_espectrales
                (punto_id,imagen_id,b2_blue,b3_green,b4_red,b8_nir,b11_swir1,b12_swir2,ndvi,ndmi,bsi,clase_id,es_verdad_campo,confianza_prediccion)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", row)
            counts["observaciones_espectrales"] += 1
        for row in registros:
            cursor.execute("""INSERT INTO registros_monitoreo
                (especie_id,punto_id,fecha_observacion,cantidad,notas_habitat)
                VALUES (%s,%s,%s,%s,%s)""", row)
            counts["registros_monitoreo"] += 1
        conn.commit()
        return {"message": "Seed complete (upserted — all data refreshed)", "inserted": counts}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  AREAS ACHA
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/areas-acha", status_code=201, tags=["Areas ACHA"])
async def create_area(body: dict):
    if "id" not in body:
        raise HTTPException(status_code=422, detail="'id' is required.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO areas_acha (id,nombre,geometria_poligonal,prioridad_muestreo) VALUES (%s,%s,%s,%s)",
            (body["id"], body.get("nombre"), body.get("geometria_poligonal"), body.get("prioridad_muestreo")))
        conn.commit()
        cursor.execute("SELECT * FROM areas_acha WHERE id=%s", (body["id"],))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=409 if e.errno==1062 else 400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/areas-acha", tags=["Areas ACHA"])
def list_areas(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM areas_acha LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/areas-acha/{area_id}", tags=["Areas ACHA"])
def get_area(area_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM areas_acha WHERE id=%s", (area_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Area {area_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/areas-acha/{area_id}", tags=["Areas ACHA"])
async def update_area(area_id: int, body: dict):
    fields = {k: v for k, v in body.items() if k in {"nombre","geometria_poligonal","prioridad_muestreo"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE areas_acha SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[area_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Area {area_id} not found.")
        cursor.execute("SELECT * FROM areas_acha WHERE id=%s", (area_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/areas-acha/{area_id}", status_code=204, tags=["Areas ACHA"])
def delete_area(area_id: int):
    """Cascade: removes observaciones + registros via puntos, then puntos, then area."""
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM puntos_muestreo WHERE area_id=%s", (area_id,))
        punto_ids = [r[0] for r in cursor.fetchall()]
        if punto_ids:
            fmt = ",".join(["%s"]*len(punto_ids))
            cursor.execute(f"DELETE FROM observaciones_espectrales WHERE punto_id IN ({fmt})", punto_ids)
            cursor.execute(f"DELETE FROM registros_monitoreo WHERE punto_id IN ({fmt})", punto_ids)
            cursor.execute(f"DELETE FROM puntos_muestreo WHERE id IN ({fmt})", punto_ids)
        cursor.execute("DELETE FROM areas_acha WHERE id=%s", (area_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Area {area_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=fk_msg(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  CATALOGO BIOMAS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/catalogo-biomas", status_code=201, tags=["Catalogo Biomas"])
async def create_bioma(body: dict):
    if "id" not in body: raise HTTPException(status_code=422, detail="'id' is required.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO catalogo_biomas (id,nombre_clase,descripcion_ecologica) VALUES (%s,%s,%s)",
            (body["id"], body.get("nombre_clase"), body.get("descripcion_ecologica")))
        conn.commit()
        cursor.execute("SELECT * FROM catalogo_biomas WHERE id=%s", (body["id"],))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=409 if e.errno==1062 else 400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/catalogo-biomas", tags=["Catalogo Biomas"])
def list_biomas(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM catalogo_biomas LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/catalogo-biomas/{bioma_id}", tags=["Catalogo Biomas"])
def get_bioma(bioma_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM catalogo_biomas WHERE id=%s", (bioma_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Bioma {bioma_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/catalogo-biomas/{bioma_id}", tags=["Catalogo Biomas"])
async def update_bioma(bioma_id: int, body: dict):
    fields = {k: v for k, v in body.items() if k in {"nombre_clase","descripcion_ecologica"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE catalogo_biomas SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[bioma_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Bioma {bioma_id} not found.")
        cursor.execute("SELECT * FROM catalogo_biomas WHERE id=%s", (bioma_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/catalogo-biomas/{bioma_id}", status_code=204, tags=["Catalogo Biomas"])
def delete_bioma(bioma_id: int):
    """Cascade: removes observaciones_espectrales linked to this clase first."""
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM observaciones_espectrales WHERE clase_id=%s", (bioma_id,))
        cursor.execute("DELETE FROM catalogo_biomas WHERE id=%s", (bioma_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Bioma {bioma_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=fk_msg(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  ESPECIES
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/especies", status_code=201, tags=["Especies"])
async def create_especie(body: dict):
    if "id" not in body: raise HTTPException(status_code=422, detail="'id' is required.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO especies (id,nombre_cientifico,estado_uicn) VALUES (%s,%s,%s)",
            (body["id"], body.get("nombre_cientifico"), body.get("estado_uicn")))
        conn.commit()
        cursor.execute("SELECT * FROM especies WHERE id=%s", (body["id"],))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=409 if e.errno==1062 else 400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/especies", tags=["Especies"])
def list_especies(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM especies LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/especies/{especie_id}", tags=["Especies"])
def get_especie(especie_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM especies WHERE id=%s", (especie_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Especie {especie_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/especies/{especie_id}", tags=["Especies"])
async def update_especie(especie_id: int, body: dict):
    fields = {k: v for k, v in body.items() if k in {"nombre_cientifico","estado_uicn"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE especies SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[especie_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Especie {especie_id} not found.")
        cursor.execute("SELECT * FROM especies WHERE id=%s", (especie_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/especies/{especie_id}", status_code=204, tags=["Especies"])
def delete_especie(especie_id: int):
    """Cascade: removes registros_monitoreo linked to this especie first."""
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM registros_monitoreo WHERE especie_id=%s", (especie_id,))
        cursor.execute("DELETE FROM especies WHERE id=%s", (especie_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Especie {especie_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=fk_msg(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  CATALOGO IMAGENES  (PK = id_producto varchar)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/catalogo-imagenes", status_code=201, tags=["Catalogo Imagenes"])
async def create_imagen(body: dict):
    if "id_producto" not in body: raise HTTPException(status_code=422, detail="'id_producto' is required.")
    if "fecha_adquisicion" not in body: raise HTTPException(status_code=422, detail="'fecha_adquisicion' is required.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO catalogo_imagenes (id_producto,fecha_adquisicion,porcentaje_nubes,sensor) VALUES (%s,%s,%s,%s)",
            (body["id_producto"], body["fecha_adquisicion"], body.get("porcentaje_nubes"), body.get("sensor")))
        conn.commit()
        cursor.execute("SELECT * FROM catalogo_imagenes WHERE id_producto=%s", (body["id_producto"],))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=409 if e.errno==1062 else 400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/catalogo-imagenes", tags=["Catalogo Imagenes"])
def list_imagenes(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM catalogo_imagenes LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/catalogo-imagenes/{id_producto}", tags=["Catalogo Imagenes"])
def get_imagen(id_producto: str):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM catalogo_imagenes WHERE id_producto=%s", (id_producto,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Imagen '{id_producto}' not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/catalogo-imagenes/{id_producto}", tags=["Catalogo Imagenes"])
async def update_imagen(id_producto: str, body: dict):
    fields = {k: v for k, v in body.items() if k in {"fecha_adquisicion","porcentaje_nubes","sensor"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE catalogo_imagenes SET {', '.join(f'{k}=%s' for k in fields)} WHERE id_producto=%s", list(fields.values())+[id_producto])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Imagen '{id_producto}' not found.")
        cursor.execute("SELECT * FROM catalogo_imagenes WHERE id_producto=%s", (id_producto,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/catalogo-imagenes/{id_producto}", status_code=204, tags=["Catalogo Imagenes"])
def delete_imagen(id_producto: str):
    """Cascade: removes observaciones_espectrales linked to this imagen first."""
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM observaciones_espectrales WHERE imagen_id=%s", (id_producto,))
        cursor.execute("DELETE FROM catalogo_imagenes WHERE id_producto=%s", (id_producto,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Imagen '{id_producto}' not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=fk_msg(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  PUNTOS MUESTREO
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/puntos-muestreo", status_code=201, tags=["Puntos Muestreo"])
async def create_punto(body: dict):
    for f in ("id","latitud","longitud"):
        if f not in body: raise HTTPException(status_code=422, detail=f"'{f}' is required.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO puntos_muestreo (id,area_id,latitud,longitud,altitud,pixel_id_hash) VALUES (%s,%s,%s,%s,%s,%s)",
            (body["id"], body.get("area_id"), body["latitud"], body["longitud"], body.get("altitud"), body.get("pixel_id_hash")))
        conn.commit()
        cursor.execute("SELECT * FROM puntos_muestreo WHERE id=%s", (body["id"],))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=409 if e.errno==1062 else 400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/puntos-muestreo", tags=["Puntos Muestreo"])
def list_puntos(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM puntos_muestreo LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/puntos-muestreo/{punto_id}", tags=["Puntos Muestreo"])
def get_punto(punto_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM puntos_muestreo WHERE id=%s", (punto_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Punto {punto_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/puntos-muestreo/{punto_id}", tags=["Puntos Muestreo"])
async def update_punto(punto_id: int, body: dict):
    fields = {k: v for k, v in body.items() if k in {"area_id","latitud","longitud","altitud","pixel_id_hash"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE puntos_muestreo SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[punto_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Punto {punto_id} not found.")
        cursor.execute("SELECT * FROM puntos_muestreo WHERE id=%s", (punto_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/puntos-muestreo/{punto_id}", status_code=204, tags=["Puntos Muestreo"])
def delete_punto(punto_id: int):
    """Cascade: removes observaciones_espectrales + registros_monitoreo linked to this punto first."""
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM observaciones_espectrales WHERE punto_id=%s", (punto_id,))
        cursor.execute("DELETE FROM registros_monitoreo WHERE punto_id=%s", (punto_id,))
        cursor.execute("DELETE FROM puntos_muestreo WHERE id=%s", (punto_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Punto {punto_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=fk_msg(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  OBSERVACIONES ESPECTRALES  (PK = id bigint auto_increment)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/observaciones-espectrales", status_code=201, tags=["Observaciones Espectrales"])
async def create_observacion(body: dict):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO observaciones_espectrales
            (punto_id,imagen_id,b2_blue,b3_green,b4_red,b8_nir,b11_swir1,b12_swir2,
             ndvi,ndmi,bsi,clase_id,es_verdad_campo,confianza_prediccion)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (body.get("punto_id"), body.get("imagen_id"),
             body.get("b2_blue"), body.get("b3_green"), body.get("b4_red"),
             body.get("b8_nir"), body.get("b11_swir1"), body.get("b12_swir2"),
             body.get("ndvi"), body.get("ndmi"), body.get("bsi"),
             body.get("clase_id"), body.get("es_verdad_campo"), body.get("confianza_prediccion")))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM observaciones_espectrales WHERE id=%s", (new_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/observaciones-espectrales", tags=["Observaciones Espectrales"])
def list_observaciones(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM observaciones_espectrales LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/observaciones-espectrales/{obs_id}", tags=["Observaciones Espectrales"])
def get_observacion(obs_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM observaciones_espectrales WHERE id=%s", (obs_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Observacion {obs_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/observaciones-espectrales/{obs_id}", tags=["Observaciones Espectrales"])
async def update_observacion(obs_id: int, body: dict):
    allowed = {"punto_id","imagen_id","b2_blue","b3_green","b4_red","b8_nir","b11_swir1","b12_swir2","ndvi","ndmi","bsi","clase_id","es_verdad_campo","confianza_prediccion"}
    fields = {k: v for k, v in body.items() if k in allowed and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE observaciones_espectrales SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[obs_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Observacion {obs_id} not found.")
        cursor.execute("SELECT * FROM observaciones_espectrales WHERE id=%s", (obs_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/observaciones-espectrales/{obs_id}", status_code=204, tags=["Observaciones Espectrales"])
def delete_observacion(obs_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM observaciones_espectrales WHERE id=%s", (obs_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Observacion {obs_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTROS MONITOREO  (PK = id bigint auto_increment)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/registros-monitoreo", status_code=201, tags=["Registros Monitoreo"])
async def create_registro(body: dict):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO registros_monitoreo
            (especie_id,punto_id,fecha_observacion,cantidad,notas_habitat)
            VALUES (%s,%s,%s,%s,%s)""",
            (body.get("especie_id"), body.get("punto_id"),
             body.get("fecha_observacion"), body.get("cantidad"), body.get("notas_habitat")))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM registros_monitoreo WHERE id=%s", (new_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e:
        conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.get("/registros-monitoreo", tags=["Registros Monitoreo"])
def list_registros(skip: int = 0, limit: int = 100):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM registros_monitoreo LIMIT %s OFFSET %s", (limit, skip))
        return rows_to_list(cursor)
    finally: cursor.close(); conn.close()

@app.get("/registros-monitoreo/{registro_id}", tags=["Registros Monitoreo"])
def get_registro(registro_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM registros_monitoreo WHERE id=%s", (registro_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=404, detail=f"Registro {registro_id} not found.")
        return row_to_dict(cursor, row)
    finally: cursor.close(); conn.close()

@app.put("/registros-monitoreo/{registro_id}", tags=["Registros Monitoreo"])
async def update_registro(registro_id: int, body: dict):
    fields = {k: v for k, v in body.items() if k in {"especie_id","punto_id","fecha_observacion","cantidad","notas_habitat"} and v is not None}
    if not fields: raise HTTPException(status_code=422, detail="No valid fields.")
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE registros_monitoreo SET {', '.join(f'{k}=%s' for k in fields)} WHERE id=%s", list(fields.values())+[registro_id])
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Registro {registro_id} not found.")
        cursor.execute("SELECT * FROM registros_monitoreo WHERE id=%s", (registro_id,))
        return row_to_dict(cursor, cursor.fetchone())
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()

@app.delete("/registros-monitoreo/{registro_id}", status_code=204, tags=["Registros Monitoreo"])
def delete_registro(registro_id: int):
    conn = get_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM registros_monitoreo WHERE id=%s", (registro_id,))
        conn.commit()
        if cursor.rowcount==0: raise HTTPException(status_code=404, detail=f"Registro {registro_id} not found.")
    except Error as e: conn.rollback(); raise HTTPException(status_code=400, detail=str(e))
    finally: cursor.close(); conn.close()
