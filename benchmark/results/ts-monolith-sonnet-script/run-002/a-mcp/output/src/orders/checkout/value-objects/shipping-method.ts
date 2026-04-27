import { Money } from '../../../shared/value-objects/money';

export interface ShippingMethod {
  name: string;
  cost: Money;
}
