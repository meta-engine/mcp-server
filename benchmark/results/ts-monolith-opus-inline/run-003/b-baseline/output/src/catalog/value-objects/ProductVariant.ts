import { Money } from "../../shared/value-objects/Money";
import { Sku } from "./Sku";

/** Variant of a product (sku + price + stock). */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
