import { Id } from "../../shared/value-objects/Id";
import { Timestamp } from "../../shared/value-objects/Timestamp";

/** Marketing-facing product description. */
export interface ProductDescription {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
