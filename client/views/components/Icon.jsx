import React from 'react'
import { string } from 'prop-types'
import {
  Home,
  Paperclip,
  Search,
  Share2,
  Globe,
  Youtube,
  BookOpen,
  Gift,
  Inbox,
  Mail,
  MessageCircle,
  GitHub,
  Frown,
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  Tag,
  FileText,
  UserPlus,
  LogIn,
  // temporary home page
  Users,
  Eye,
} from 'react-feather'
import get from 'lodash.get'

const MAP = {
  home: Home,
  terms: Paperclip,
  search: Search,
  adapt: Share2,
  open: Globe,
  video: Youtube,
  docs: BookOpen,
  stories: Gift,
  updates: Inbox,
  contact: Mail,
  talk: MessageCircle,
  github: GitHub,
  error: Frown,
  up: ThumbsUp,
  down: ThumbsDown,
  check: CheckCircle,
  subject: Tag,
  card: FileText,
  signUp: UserPlus,
  logIn: LogIn,
  // temporary home page
  view: Eye,
  friends: Users,
}

const SIZES = {
  s: 14,
  m: 16,
  l: 16,
  xl: 16,
  xxl: 32,
}

export default function Icon({ i, s = 'm' }) {
  return (
    <i className={`Icon icon-${i}`}>
      {React.createElement(get(MAP, i, 'span'), { size: get(SIZES, s) })}
    </i>
  )
}

Icon.propTypes = {
  i: string.isRequired,
  s: string,
}

Icon.defaultProps = {
  s: 'm',
}
