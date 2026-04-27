import { Money } from '../../shared/value-objects/Money';
import { Sku } from './Sku';

/** Specific variant of a product with its own SKU and stock level */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
