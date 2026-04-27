import { Sku } from "./Sku";
import { Money } from "../../shared/value-objects/Money";

/** Sellable variant of a product with its own price and stock level. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
