import { Money } from '../../../shared/value-objects/money';

export interface CartDiscount {
  code: string;
  amount: Money;
}
