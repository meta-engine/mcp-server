import { Money } from '../../../shared/value-objects/Money';

/** Available shipping option with its cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
