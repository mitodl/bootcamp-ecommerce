// @flow
import React, { useState } from "react"
import { useSelector } from "react-redux"
import { useRequest } from "redux-query-react"
import {
  Collapse,
  Navbar,
  Nav,
  NavbarBrand,
  NavbarToggler,
  NavItem
} from "reactstrap"

import queries from "../lib/queries"
import { currentUserSelector } from "../lib/queries/users"
import { routes } from "../lib/urls"

const navbarCollapseSize = "md"

export const SiteNavbar = () => {
  useRequest(queries.users.currentUserQuery())
  const currentUser = useSelector(currentUserSelector)

  const [isOpen, setIsOpen] = useState(false)
  const toggle = () => setIsOpen(!isOpen)

  if (!currentUser) {
    return null
  }

  return (
    <div className="nav-wrapper">
      <Navbar
        expand={navbarCollapseSize}
        className="container d-flex align-items-center"
      >
        <NavbarBrand tag="div" className="flex-grow-1">
          <a className="brand-logo" href={routes.root}>
            <img
              src="/static/images/bootcamp-logo.svg"
              alt="MIT Bootcamps Logo"
            />
          </a>
          <a
            className="btn-styled btn-red size-1"
            href={routes.applications.dashboard}
            aria-label="Apply"
          >
            Apply Now
          </a>
        </NavbarBrand>
        <NavbarToggler
          onClick={toggle}
          className={`p-0 d-flex d-${navbarCollapseSize}-none`}
        >
          <i className="material-icons">menu</i>
        </NavbarToggler>
        <Collapse isOpen={isOpen} navbar>
          <Nav navbar className="flex-row flex-grow-1 justify-content-end">
            <NavItem>
              <a className="text-link" href={routes.resourcePages.howToApply}>
                How to Apply
              </a>
            </NavItem>
            {currentUser.is_anonymous ? (
              <React.Fragment>
                <NavItem>
                  <a
                    className="btn-styled btn-dk-grey size-1"
                    href={routes.login}
                  >
                    Sign In
                  </a>
                </NavItem>
                <NavItem>
                  <a
                    className="btn-styled btn-dk-grey size-1"
                    href={routes.register}
                  >
                    Create Account
                  </a>
                </NavItem>
              </React.Fragment>
            ) : (
              <NavItem>
                <a
                  className="btn-styled btn-dk-grey size-1"
                  href={routes.logout}
                >
                  Sign Out
                </a>
              </NavItem>
            )}
          </Nav>
        </Collapse>
      </Navbar>
    </div>
  )
}

export default SiteNavbar
