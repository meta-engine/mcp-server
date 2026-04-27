import { Money } from '../../../shared/value-objects/Money';

/** Represents a discount applied to a cart. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
