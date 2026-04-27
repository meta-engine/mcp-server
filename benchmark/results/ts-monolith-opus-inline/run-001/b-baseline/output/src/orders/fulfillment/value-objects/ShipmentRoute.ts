import { Id } from "../../../shared/value-objects/Id";
import { Timestamp } from "../../../shared/value-objects/Timestamp";

/** Routing metadata for a shipment. */
export interface ShipmentRoute {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
