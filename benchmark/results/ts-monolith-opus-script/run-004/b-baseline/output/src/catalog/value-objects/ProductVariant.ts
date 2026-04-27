import { Money } from "../../shared/value-objects/Money";
import { Sku } from "./Sku";

/** ProductVariant value object. */
export interface ProductVariant {
  sku: Sku;
  price: Money;
  stockLevel: number;
}
