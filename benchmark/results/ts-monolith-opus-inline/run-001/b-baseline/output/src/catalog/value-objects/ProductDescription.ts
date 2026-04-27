import { Id } from "../../shared/value-objects/Id";
import { Timestamp } from "../../shared/value-objects/Timestamp";

/** Editable descriptive content attached to a product. */
export interface ProductDescription {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
