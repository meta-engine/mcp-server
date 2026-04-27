import { Sku } from './Sku';
import { Money } from '../../shared/value-objects/Money';

/** A specific variant of a product with its own SKU and price. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
