Feature: unlink

  Scenario: unlink sub command do nothing until execute symlink
    Given there are dotfiles home directory in dotfiles
    And dotfav is initialized
    And dotfiles home directory contains no files
    And home directory contains some files
    When we run dotfav unlink
    Then home directory does not changed

  Scenario: unlink sub command removes the files symlinked by dotfav
    Given there are dotfiles home directory in dotfiles
    And dotfav is initialized
    And dotfiles home directory contains a file named "file"
    And home directory contains some files
    When we run dotfav symlink
    And we run dotfav unlink
    Then home directory does not changed
