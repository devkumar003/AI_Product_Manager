import logging
import uuid
import hashlib
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.development import GitBranch, GitCommit, GitPullRequest
from app.services.ai.llm_manager import llm_manager
from app.services.ai.agents.base import AgentConfig

logger = logging.getLogger("app.services.development.git_workflow")


class GitWorkflow:
    def create_branch(
        self, db: Session, workspace_id: UUID, branch_name: str, source_branch: str = "main"
    ) -> GitBranch:
        """
        Creates a Git branch inside the Workspace simulation environment.
        """
        logger.info(f"Creating Git branch: {branch_name} from {source_branch}")
        branch = GitBranch(
            workspace_id=workspace_id,
            branch_name=branch_name,
            source_branch=source_branch,
            status="Active"
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    def commit_changes(
        self, 
        db: Session, 
        workspace_id: UUID, 
        branch_id: UUID, 
        commit_message: str, 
        files_changed: list[str]
    ) -> GitCommit:
        """
        Records a Git commit in the workspace context database.
        """
        logger.info(f"Recording commit on branch: {branch_id}")
        
        # Calculate mock hash
        sha = hashlib.sha1()
        sha.update(f"{branch_id}-{commit_message}-{datetime.utcnow().isoformat()}".encode('utf-8'))
        commit_hash = sha.hexdigest()

        commit = GitCommit(
            workspace_id=workspace_id,
            branch_id=branch_id,
            commit_hash=commit_hash,
            commit_message=commit_message,
            author="AI Developer Agent",
            files_changed=files_changed
        )
        db.add(commit)
        db.commit()
        db.refresh(commit)
        return commit

    def generate_pull_request(
        self,
        db: Session,
        workspace_id: UUID,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str = "main"
    ) -> GitPullRequest:
        """
        Creates a pull request and queries the LLM for merge recommendations/suggestions.
        """
        logger.info(f"Generating PR: {title} from {source_branch} to {target_branch}")
        system_prompt = "You are a Senior Release Engineer. Analyze branches and recommend merge safety."
        llm_prompt = (
            f"Review the pull request details:\n"
            f"PR Title: {title}\n"
            f"PR Description: {description}\n"
            f"Merging: {source_branch} -> {target_branch}\n\n"
            f"Provide a merge safety recommendation: Ready, Conflicts, or ReviewRequired."
        )

        try:
            res = llm_manager.generate_sync(
                prompt=llm_prompt,
                system_prompt=system_prompt,
                config=AgentConfig(temperature=0.1)
            )
            content = res.content.lower()
            if "conflict" in content:
                recommendation = "Conflicts"
            elif "review" in content or "required" in content:
                recommendation = "ReviewRequired"
            else:
                recommendation = "Ready"
        except Exception:
            recommendation = "Ready"

        pr = GitPullRequest(
            workspace_id=workspace_id,
            title=title,
            description=description,
            source_branch=source_branch,
            target_branch=target_branch,
            status="Open",
            merge_recommendation=recommendation
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        return pr

    def merge_pull_request(self, db: Session, workspace_id: UUID, pr_id: UUID) -> GitPullRequest | None:
        pr = db.query(GitPullRequest).filter(
            GitPullRequest.id == pr_id, 
            GitPullRequest.workspace_id == workspace_id
        ).first()
        if pr:
            pr.status = "Merged"
            db.commit()
            db.refresh(pr)
        return pr


git_workflow = GitWorkflow()
