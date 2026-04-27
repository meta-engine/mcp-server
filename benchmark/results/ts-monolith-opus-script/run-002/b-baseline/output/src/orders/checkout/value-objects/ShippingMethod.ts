import { Money } from "../../../shared/value-objects/Money";

/** Selectable shipping option with cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
