import { Money } from '../../../shared/value-objects/Money';

/** ShippingMethod value object representing a shipping option and its cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
