"""Sistema de limpieza automática para retos expirados"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import threading
import schedule

from bson.objectid import ObjectId
from util.load_data import get_mongo_data


class RetoCleanupService:
    """Servicio para limpieza automática de retos expirados"""

    def __init__(self):
        self.retos_collection = get_mongo_data("retos")
        self.publicaciones_collection = get_mongo_data("publicacion")
        self.is_running = False

    async def cleanup_expired_challenges(self) -> Dict[str, Any]:
        """Limpia los retos expirados y sus publicaciones
        
        Returns:
            Dict con estadísticas de la limpieza
        """
        try:

            retos_expirados = self.retos_collection.find({
                "fecha_expiracion": {"$lt": datetime.now()},
                "activo": True
            })

            publicaciones_eliminadas = 0
            retos_marcados_inactivos = 0

            for reto in retos_expirados:

                publicaciones_ids = reto.get("publicaciones", [])
                if publicaciones_ids:

                    result = self.publicaciones_collection.delete_many({
                        "_id": {"$in": [ObjectId(pid) for pid in publicaciones_ids]}
                    })
                    publicaciones_eliminadas += result.deleted_count

                self.retos_collection.update_one(
                    {"_id": reto["_id"]},
                    {"$set": {"activo": False}}
                )
                retos_marcados_inactivos += 1

            return {
                "success": True,
                "retos_marcados_inactivos": retos_marcados_inactivos,
                "publicaciones_eliminadas": publicaciones_eliminadas,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def schedule_cleanup(self):
        """Programa la limpieza automática"""

        schedule.every().day.at("02:00").do(
            lambda: asyncio.create_task(self.cleanup_expired_challenges())
        )

        schedule.every(6).hours.do(
            lambda: asyncio.create_task(self.cleanup_expired_challenges())
        )

    async def start_scheduler(self):
        """Inicia el programador de tareas"""
        if self.is_running:
            return

        self.is_running = True
        self.schedule_cleanup()

        print("🔄 Servicio de limpieza de retos iniciado")
        print("📅 Limpieza programada: diaria a las 2:00 AM y cada 6 horas")

        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(60)

    def stop_scheduler(self):
        """Detiene el programador de tareas"""
        self.is_running = False
        schedule.clear()
        print("⏹️ Servicio de limpieza de retos detenido")

cleanup_service = RetoCleanupService()


async def run_cleanup_service():
    """Función para ejecutar el servicio de limpieza"""
    await cleanup_service.start_scheduler()


def start_cleanup_service():
    """Inicia el servicio de limpieza en un hilo separado"""


    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_cleanup_service())

    cleanup_thread = threading.Thread(target=run_async, daemon=True)
    cleanup_thread.start()
    return cleanup_thread


if __name__ == "__main__":
    asyncio.run(cleanup_service.cleanup_expired_challenges())
