import { EmailTemplate } from "../value-objects/EmailTemplate";
import { Id } from "../../shared/value-objects/Id";

/** CRUD operations for notification templates. */
export class NotificationService {
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
