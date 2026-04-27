import { Sku } from './sku';
import { Money } from '../../shared/value-objects/money';

export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
