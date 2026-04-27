import { Money } from "../../../shared/value-objects/Money";

/** ShippingMethod value object. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
