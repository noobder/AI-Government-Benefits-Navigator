import { useTranslation } from "react-i18next";
import type { DocumentItem } from "../types/scheme";

export default function DocumentChecklist({ documents }: { documents: DocumentItem[] }) {
  const { t } = useTranslation();
  if (documents.length === 0) {
    return <p className="text-sm text-[var(--ink-muted)]">{t("scheme.noDocumentsOnRecord")}</p>;
  }
  return (
    <ul className="space-y-2">
      {documents.map((doc, i) => (
        <li key={i} className="flex items-start gap-2 text-sm">
          <span aria-hidden>{doc.status === "required" ? "☑" : "☐"}</span>
          <span>
            {doc.name}
            {doc.status === "possibly_required" && (
              <span className="ml-1 text-xs text-[var(--ink-muted)]">{t("scheme.possiblyRequired")}</span>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}
