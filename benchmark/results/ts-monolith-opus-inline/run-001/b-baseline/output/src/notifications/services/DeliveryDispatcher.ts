import { Id } from "../../shared/value-objects/Id";
import { EmailTemplate } from "../value-objects/EmailTemplate";

/** Dispatches notifications across configured channels. */
export class DeliveryDispatcher {
  create(input: Partial<EmailTemplate>): EmailTemplate {
    void input;
    throw new Error("not implemented");
  }

  findById(id: Id): EmailTemplate | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): EmailTemplate[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: Id): void {
    void id;
    throw new Error("not implemented");
  }
}
