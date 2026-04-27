import { Sku } from "./Sku";
import { Money } from "../../shared/value-objects/Money";

/** ProductVariant value object. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
