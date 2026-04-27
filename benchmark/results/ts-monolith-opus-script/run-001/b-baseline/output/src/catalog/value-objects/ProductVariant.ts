import { Money } from '../../shared/value-objects/Money';
import { Sku } from './Sku';

/** ProductVariant value object capturing a sellable variant of a product. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
