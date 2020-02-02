"""Handler for applying branch protections settings.

See https://developer.github.com/v3/repos/branches/#update-branch-protection for all available settings.
"""
import logging

from github import GithubException
from github.Consts import mediaTypeRequireMultipleApprovingReviews

from .._util import HandlerRequest

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(request: HandlerRequest):
    """Manage branch protection rules.

    .. code-block:: yaml

        branches:
          - name: master
            # https://developer.github.com/v3/repos/branches/#update-branch-protection
            # Branch Protection settings. Set to null to disable
            protection:
              # Required. Require at least one approving review on a pull request, before merging.
              # Set to null to disable.
              required_pull_request_reviews:
                # The number of approvals required. (1-6)
                required_approving_review_count: 1
                # Dismiss approved reviews automatically when a new commit is pushed.
                dismiss_stale_reviews: true
                # Blocks merge until code owners have reviewed.
                require_code_owner_reviews: true
                # Specify which users and teams can dismiss pull request reviews.
                # Pass an empty dismissal_restrictions object to disable.
                # User and team dismissal_restrictions are only available for organization-owned repositories.
                # Omit this parameter for personal repositories.
                dismissal_restrictions:
                  users: []
                  teams: []
              # Required. Require status checks to pass before merging. Set to null to disable
              required_status_checks:
                # Required. Require branches to be up to date before merging.
                strict: true
                # Required. The list of status checks to require in order to merge into this branch
                contexts: []
              # Required. Enforce all configured restrictions for administrators.
              # Set to true to enforce required status checks for repository administrators.
              # Set to null to disable.
              enforce_admins: true
              # Required. Restrict who can push to this branch.
              # Team and user restrictions are only available for organization-owned repositories.
              # Set to null to disable.
              restrictions:
                apps: []
                users: []
                teams: []

    """

    _LOGGER.info("Applying branch protection settings")
    _LOGGER.info("Branch protection configuration:\n%s", request.data)

    for branch_config in request.data:
        _LOGGER.info("Updating branch protection for branch '%s'", branch_config["name"])
        try:
            branch = request.repository.get_branch(branch_config["name"])
        except GithubException as error:
            if error.data.get("message") == "Branch not found":
                _LOGGER.warning(
                    "Branch protection requested for non-existant branch '%s'. Skipping.",
                    branch_config["name"],
                )
                continue
            raise
        # branch.edit_protection(**branch_config["protection"])
        # edit_protection is a custom wrapper on top of update_branch_protection
        # https://github.com/mattsb42/repo-manager/issues/17
        branch._requester.requestJsonAndCheck(  # remove once #17 is fixed pylint: disable=protected-access
            "PUT",
            branch.protection_url,
            headers={"Accept": mediaTypeRequireMultipleApprovingReviews},
            input=branch_config["protection"],
        )
