import { Money } from '../../shared/value-objects/Money';
import { Sku } from './Sku';

/** ProductVariant value object representing a variant of a product. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
