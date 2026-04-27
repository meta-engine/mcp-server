import { Money } from '../../shared/value-objects/Money';
import { Sku } from './Sku';

/** ProductVariant value object */
export interface ProductVariant {
  readonly sku: Sku;
  readonly price: Money;
  readonly stockLevel: number;
}
