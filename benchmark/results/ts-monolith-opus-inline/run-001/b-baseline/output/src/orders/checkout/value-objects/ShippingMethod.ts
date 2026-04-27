import { Money } from "../../../shared/value-objects/Money";

/** A selectable shipping option offered at checkout. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
