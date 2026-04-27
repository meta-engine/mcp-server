import { Money } from "../../shared/value-objects/Money";
import { Sku } from "./Sku";

/** A purchasable variant of a product. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
