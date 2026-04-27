import { Money } from '../../../shared/value-objects/Money';

/** A shipping option with associated cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
