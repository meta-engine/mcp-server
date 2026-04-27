import { Money } from '../../../shared/value-objects/Money';

/** ShippingMethod value object */
export interface ShippingMethod {
  readonly name: string;
  readonly cost: Money;
}
