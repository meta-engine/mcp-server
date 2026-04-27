import { Money } from "../../../shared/value-objects/Money";

/** Shipping method available at checkout. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
