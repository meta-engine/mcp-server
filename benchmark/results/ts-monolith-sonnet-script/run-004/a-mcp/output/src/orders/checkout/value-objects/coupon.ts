import { Money } from '../../../shared/value-objects/money';

export interface Coupon {
  code: string;
  discount: Money;
}
