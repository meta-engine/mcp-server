import { Money } from '../../shared/value-objects/Money';
import { Sku } from './Sku';

/** A specific variant of a product with its own price and stock level. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
