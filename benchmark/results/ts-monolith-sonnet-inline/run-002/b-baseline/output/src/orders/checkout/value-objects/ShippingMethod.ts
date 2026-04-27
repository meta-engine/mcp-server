import { Money } from '../../../shared/value-objects/Money';

/** Available shipping method with its associated cost. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
