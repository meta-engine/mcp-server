import { Id } from "../../shared/value-objects/Id";
import { Timestamp } from "../../shared/value-objects/Timestamp";

/** Descriptive metadata associated with a product. */
export interface ProductDescription {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
