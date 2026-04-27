import { Money } from '../../../shared/value-objects/Money';

/** Represents a shipping method with its cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
