import { PaymentMethodKind } from '../enums/payment-method-kind.enum';

export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
