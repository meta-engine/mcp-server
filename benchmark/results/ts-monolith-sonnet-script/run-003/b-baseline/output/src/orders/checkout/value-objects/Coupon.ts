import { Money } from '../../../shared/value-objects/Money';

/** Coupon value object */
export interface Coupon {
  readonly code: string;
  readonly discount: Money;
}
