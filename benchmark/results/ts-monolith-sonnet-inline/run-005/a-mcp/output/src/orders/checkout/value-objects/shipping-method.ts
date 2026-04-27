import { Money } from '../../../shared/value-objects/money';

/** ShippingMethod value object. */
export interface ShippingMethod {
  name: string;
  cost: Money;
}
