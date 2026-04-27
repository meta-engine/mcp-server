import { Id } from "../../../shared/value-objects/Id";
import { Timestamp } from "../../../shared/value-objects/Timestamp";

/** Named route used to plan shipments. */
export interface ShipmentRoute {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
