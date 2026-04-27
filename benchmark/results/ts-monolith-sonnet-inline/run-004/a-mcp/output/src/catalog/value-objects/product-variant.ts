import { Sku } from './sku';
import { Money } from '../../shared/value-objects/money';

/** ProductVariant value object. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
