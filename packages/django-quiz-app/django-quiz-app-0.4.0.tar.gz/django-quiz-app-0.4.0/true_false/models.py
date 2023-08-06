from django.db import models
from quiz.models import Question


class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Tick this if the question "
                                            "is true. Leave it blank for"
                                            " false.")

    def check_if_correct(self, guess):
        if guess == "T":
            guess_bool = True
        elif guess == "F":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct('T'),
                 'content': 'True'},
                {'correct': self.check_if_correct('F'),
                 'content': 'False'}]

    class Meta:
        verbose_name = "True/False Question"
        verbose_name_plural = "True/False Questions"
        ordering = ['category']

    def __unicode__(self):
        return unicode(self.content)
