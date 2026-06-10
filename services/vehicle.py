"""Vehicle service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle, VehicleDocument, VehicleStatus
from app.repositories.vehicle import VehicleRepository, VehicleDocumentRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleDocumentCreate, VehicleDocumentUpdate


class VehicleService:
    """Service for vehicle operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = VehicleRepository(session)
        self.document_repository = VehicleDocumentRepository(session)

    def create_vehicle(
        self,
        vehicle_data: VehicleCreate,
        owner_id: str,
        company_id: Optional[str] = None,
    ) -> Vehicle:
        """Create a new vehicle."""
        # Check if registration number already exists
        existing_vehicle = self.repository.get_by_registration_number(
            vehicle_data.registration_number
        )
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this registration number already exists"
            )

        payload = vehicle_data.model_dump()
        payload["owner_id"] = owner_id
        if company_id:
            payload["company_id"] = company_id
        return self.repository.create(payload)

    def get_vehicle(self, vehicle_id: str, owner_id: str) -> Vehicle:
        """Get vehicle by ID."""
        vehicle = self.repository.get(vehicle_id)
        if not vehicle or vehicle.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        return vehicle

    def get_vehicles(
        self, 
        owner_id: str,
        status: Optional[VehicleStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles for owner."""
        return self.repository.get_by_owner(
            owner_id=owner_id,
            status=status,
            skip=skip,
            limit=limit
        )

    def update_vehicle(
        self, 
        vehicle_id: str, 
        vehicle_data: VehicleUpdate, 
        owner_id: str
    ) -> Vehicle:
        """Update vehicle."""
        vehicle = self.get_vehicle(vehicle_id, owner_id)
        
        # Check registration number uniqueness if being updated
        if (vehicle_data.registration_number and 
            vehicle_data.registration_number != vehicle.registration_number):
            existing_vehicle = self.repository.get_by_registration_number(
                vehicle_data.registration_number
            )
            if existing_vehicle and existing_vehicle.id != vehicle_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle with this registration number already exists"
                )

        update_data = vehicle_data.dict(exclude_unset=True)
        return self.repository.update(vehicle, update_data)

    def delete_vehicle(self, vehicle_id: str, owner_id: str) -> bool:
        """Soft delete vehicle."""
        vehicle = self.get_vehicle(vehicle_id, owner_id)
        return self.repository.delete(vehicle)

    def search_vehicles(
        self, 
        owner_id: str, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        """Search vehicles by registration, brand, model."""
        return self.repository.search_vehicles(
            owner_id=owner_id,
            search_term=search_term,
            skip=skip,
            limit=limit
        )

    def get_vehicles_with_expired_documents(self, owner_id: str) -> List[Vehicle]:
        """Get vehicles with expired documents."""
        return self.repository.get_vehicles_with_expired_documents(owner_id)

    def get_vehicles_due_for_service(self, owner_id: str) -> List[Vehicle]:
        """Get vehicles due for service."""
        return self.repository.get_vehicles_due_for_service(owner_id)

    def get_vehicle_stats(self, owner_id: str) -> dict:
        """Get vehicle statistics."""
        stats = self.repository.get_vehicle_stats(owner_id)
        
        # Add additional stats
        expired_docs = len(self.get_vehicles_with_expired_documents(owner_id))
        service_due = len(self.get_vehicles_due_for_service(owner_id))
        
        stats.update({
            'vehicles_with_expired_docs': expired_docs,
            'vehicles_due_for_service': service_due
        })
        
        return stats

    # Vehicle Document methods
    def create_vehicle_document(
        self, 
        document_data: VehicleDocumentCreate, 
        owner_id: str
    ) -> VehicleDocument:
        """Create vehicle document."""
        # Verify vehicle ownership
        vehicle = self.get_vehicle(document_data.vehicle_id, owner_id)
        
        document = VehicleDocument(**document_data.dict())
        return self.document_repository.create(document)

    def get_vehicle_documents(self, vehicle_id: str, owner_id: str) -> List[VehicleDocument]:
        """Get all documents for a vehicle."""
        # Verify vehicle ownership
        self.get_vehicle(vehicle_id, owner_id)
        return self.document_repository.get_by_vehicle(vehicle_id)

    def update_vehicle_document(
        self, 
        document_id: str, 
        document_data: VehicleDocumentUpdate,
        owner_id: str
    ) -> VehicleDocument:
        """Update vehicle document."""
        document = self.document_repository.get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verify vehicle ownership
        self.get_vehicle(document.vehicle_id, owner_id)
        
        update_data = document_data.dict(exclude_unset=True)
        return self.document_repository.update(document, update_data)

    def delete_vehicle_document(
        self, 
        document_id: str, 
        owner_id: str
    ) -> bool:
        """Delete vehicle document."""
        document = self.document_repository.get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verify vehicle ownership
        self.get_vehicle(document.vehicle_id, owner_id)
        
        return self.document_repository.delete(document)

    def get_expired_documents(self, owner_id: str) -> List[VehicleDocument]:
        """Get all expired documents for owner's vehicles."""
        return self.document_repository.get_expired_documents(owner_id)

    def get_expiring_documents(
        self, 
        owner_id: str, 
        days: int = 30
    ) -> List[VehicleDocument]:
        """Get documents expiring within specified days."""
        return self.document_repository.get_expiring_soon(owner_id, days)