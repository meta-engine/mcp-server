import { Money } from '../../../shared/value-objects/Money';

/** CartDiscount value object */
export interface CartDiscount {
  readonly code: string;
  readonly amount: Money;
}
