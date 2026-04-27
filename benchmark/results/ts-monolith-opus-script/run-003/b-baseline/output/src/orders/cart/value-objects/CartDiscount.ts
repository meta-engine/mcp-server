import { Money } from '../../../shared/value-objects/Money';

/** CartDiscount value object. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
