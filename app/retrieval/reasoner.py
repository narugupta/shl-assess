from app.retrieval.schema import AssessmentDocument


class RecommendationReasoner:

    def build(self, doc: AssessmentDocument, query) -> str:

        reasons = []

        if query.role:

            reasons.append(
                f"Relevant for {query.role} hiring."
            )

        if query.duration and doc.duration:

            if doc.duration <= query.duration:

                reasons.append(
                    f"Fits within the requested {query.duration}-minute limit."
                )

        if query.language and query.language in doc.languages:

            reasons.append(
                f"Available in {query.language}."
            )

        if doc.categories:

            reasons.append(
                f"Measures {', '.join(doc.categories)}."
            )

        return " ".join(reasons)